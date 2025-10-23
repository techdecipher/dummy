# lambda_function.py
import json, base64, re, urllib.request, urllib.error

# ===== HARDCODED CONFIG =====
GITHUB_TOKEN     = "ghp_your_pat_here"
GH_OWNER         = "techdecipher"
GH_REPO          = "dummy"
GH_BRANCH        = "dev"

SOURCE_DIR       = "scratch/roles/template-role"   # folder to copy FROM
DEST_PARENT_DIR  = "scratch/roles"                 # parent folder; final dest = DEST_PARENT_DIR/<iam_name>

TG_FILE_BASENAME = "terragrunt.hcl"
ROLE_ARN_PREFIX  = "arn:aws:iam::123456789012:role/"  # role_name becomes this + iam_name

COMMIT_MSG       = "scaffold role folder and update terragrunt.hcl"
# ===========================

# --- GitHub helper ---
def gh(method, url, token, body=None):
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "lambda-gh-folder-copy-hcl-edit")
    if body is not None:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(body).encode("utf-8")
    try:
        with urllib.request.urlopen(req) as r:
            t = r.read().decode("utf-8")
            return json.loads(t) if t else {}
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"GitHub {method} {url} -> {e.code}: {e.read().decode('utf-8','ignore')}")

# --- HCL edit helpers ---
_role_pat   = re.compile(r'(?m)^\s*role_name\s*=\s*".*?"\s*$')
_cpol_pat   = re.compile(r'(?m)^\s*custom_policy_name\s*=\s*".*?"\s*$')
_inputs_pat = re.compile(r'(?s)inputs\s*=\s*{')

def update_terragrunt(text: str, role_val: str, cpol_val: str) -> str:
    out = text
    found_role = bool(_role_pat.search(out))
    found_cpol = bool(_cpol_pat.search(out))
    if found_role:
        out = _role_pat.sub(f'role_name = "{role_val}"', out)
    if found_cpol:
        out = _cpol_pat.sub(f'custom_policy_name = "{cpol_val}"', out)
    if not (found_role and found_cpol):
        m = _inputs_pat.search(out)
        if m:
            brace_idx = out.find("{", m.end() - 1)
            if brace_idx != -1:
                insert_pos = brace_idx + 1
                lines = []
                if not found_role:
                    lines.append(f'\n  role_name = "{role_val}"')
                if not found_cpol:
                    lines.append(f'\n  custom_policy_name = "{cpol_val}"')
                out = out[:insert_pos] + "".join(lines) + out[insert_pos:]
    return out

# --- Base64 util ---
def b64dec_utf8(b64txt: str) -> str:
    return base64.b64decode(b64txt.replace("\n","").encode()).decode("utf-8")

# --- Safe payload parse ---
def parse_payload(event):
    if isinstance(event, dict) and "body" in event:
        return json.loads(event["body"] or "{}") if isinstance(event["body"], str) else (event["body"] or {})
    return event if isinstance(event, dict) else {}

def lambda_handler(event, context):
    p = parse_payload(event)
    # Build iam_name from event
    try:
        prefix = p["prefix"]; environment = p["environment"]; app = p["app_name"]
        role = p["role"]; stage = p["stage"]
    except KeyError as k:
        return {"statusCode": 400, "body": json.dumps({"error": f"missing key: {k.args[0]}", "required": ["prefix","environment","app_name","role","stage"]})}

    iam_name = f"{prefix}_{environment}-{app}_{role}-{stage}"
    dest_dir = f"{DEST_PARENT_DIR.strip('/')}/{iam_name}"
    policy_name = f"tbdpt-{iam_name}-rw-policy"
    role_name_value = f"{ROLE_ARN_PREFIX}{iam_name}"

    api = f"https://api.github.com/repos/{GH_OWNER}/{GH_REPO}"

    # 1) Get branch → commit
    ref = gh("GET", f"{api}/git/ref/heads/{GH_BRANCH}", GITHUB_TOKEN)
    base_commit_sha = ref["object"]["sha"]

    # 2) Commit → tree
    base_commit = gh("GET", f"{api}/git/commits/{base_commit_sha}", GITHUB_TOKEN)
    base_tree_sha = base_commit["tree"]["sha"]

    # 3) Full tree
    tree = gh("GET", f"{api}/git/trees/{base_tree_sha}?recursive=1", GITHUB_TOKEN)
    if "tree" not in tree:
        return {"statusCode": 404, "body": json.dumps({"error": "repo tree not found"})}

    src_prefix = SOURCE_DIR.strip("/") + "/"
    dst_prefix = dest_dir.strip("/") + "/"
    entries = []
    src_tg_blob_sha = None
    src_tg_fullpath = f"{SOURCE_DIR.strip('/')}/{TG_FILE_BASENAME}"
    dst_tg_fullpath = f"{dest_dir.strip('/')}/{TG_FILE_BASENAME}"

    # 4) Collect blobs under SOURCE_DIR
    for node in tree["tree"]:
        if node.get("type") == "blob" and node.get("path","").startswith(src_prefix):
            rel = node["path"][len(src_prefix):]
            entries.append({
                "path": f"{dst_prefix}{rel}",
                "mode": node.get("mode","100644"),
                "type": "blob",
                "sha": node["sha"]
            })
            if node["path"] == src_tg_fullpath:
                src_tg_blob_sha = node["sha"]

    if not entries:
        return {"statusCode": 404, "body": json.dumps({"error": f"No files found under '{SOURCE_DIR}'"})}

    # 5) Edit copied terragrunt.hcl
    if src_tg_blob_sha:
        blob = gh("GET", f"{api}/git/blobs/{src_tg_blob_sha}", GITHUB_TOKEN)
        original_text = b64dec_utf8(blob["content"]) if blob.get("encoding") == "base64" else blob.get("content","")
        edited_text = update_terragrunt(original_text, role_name_value, policy_name)
        new_blob = gh("POST", f"{api}/git/blobs", GITHUB_TOKEN, {"content": edited_text, "encoding": "utf-8"})
        # override the file at dest with edited blob
        entries = [e for e in entries if e["path"] != dst_tg_fullpath]
        entries.append({"path": dst_tg_fullpath, "mode": "100644", "type": "blob", "sha": new_blob["sha"]})

    # 6) Create tree
    new_tree = gh("POST", f"{api}/git/trees", GITHUB_TOKEN, {"base_tree": base_tree_sha, "tree": entries})
    new_tree_sha = new_tree["sha"]

    # 7) Commit
    msg = f"{COMMIT_MSG} → {iam_name}"
    new_commit = gh("POST", f"{api}/git/commits", GITHUB_TOKEN, {
        "message": msg, "tree": new_tree_sha, "parents": [base_commit_sha],
        "author": {"name":"Lambda Bot","email":"lambda@example.com"},
        "committer":{"name":"Lambda Bot","email":"lambda@example.com"}
    })
    new_commit_sha = new_commit["sha"]

    # 8) Update ref
    gh("PATCH", f"{api}/git/refs/heads/{GH_BRANCH}", GITHUB_TOKEN, {"sha": new_commit_sha, "force": False})

    return {
        "statusCode": 200,
        "body": json.dumps({
            "iam_name": iam_name,
            "copied_from": SOURCE_DIR,
            "copied_to": dest_dir,
            "terragrunt_modified": bool(src_tg_blob_sha),
            "role_name": role_name_value,
            "custom_policy_name": policy_name,
            "dest_terragrunt_path": dst_tg_fullpath,
            "commit_sha": new_commit_sha,
            "message": msg
        })
    }
