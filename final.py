# lambda_function.py
import json, base64, re, urllib.request, urllib.error

# ================== HARDCODED CONFIG ==================
GITHUB_TOKEN     = "ghp_your_pat_here"
GH_OWNER         = "your-org-or-user"
GH_REPO          = "your-repo"
GH_BRANCH        = "dev"                       # e.g., "main" or "dev"

# Copy template role folder FROM here...
SOURCE_DIR       = "scratch/roles/template-role"
# ...TO a folder named after iam_name under this parent:
DEST_PARENT_DIR  = "scratch/roles"

# terragrunt.hcl inside the role folder to edit after copy
TG_FILE_BASENAME = "terragrunt.hcl"

# The role_name we set will be: ROLE_ARN_PREFIX + iam_name
ROLE_ARN_PREFIX  = "arn:aws:iam::000000000000:role/"    # <-- put your AWS account

# The S3 terragrunt.hcl path to patch (absolute path in repo)
S3_TG_PATH       = "storage/s3/tbdp-pnp-stage-dev/terragrunt.hcl"  # <-- change to your path

COMMIT_MSG       = "scaffold role & update S3 TG with iam role"
# ======================================================


# ---------------- GitHub helper ----------------
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


# ---------------- Base64 util ----------------
def b64dec_utf8(b64txt: str) -> str:
    return base64.b64decode(b64txt.replace("\n", "").encode()).decode("utf-8")


# ---------------- Parse payload ----------------
def parse_payload(event):
    if isinstance(event, dict) and "body" in event:
        return json.loads(event["body"] or "{}") if isinstance(event["body"], str) else (event["body"] or {})
    return event if isinstance(event, dict) else {}


# ---------------- HCL edit helpers (role TG) ----------------
_role_pat   = re.compile(r'(?m)^\s*role_name\s*=\s*".*?"\s*$')
_cpol_pat   = re.compile(r'(?m)^\s*custom_policy_name\s*=\s*".*?"\s*$')
_inputs_pat = re.compile(r'(?s)inputs\s*=\s*{')

def update_role_tg(text: str, role_val: str, cpol_val: str) -> str:
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
                add = []
                if not found_role:
                    add.append(f'\n  role_name = "{role_val}"')
                if not found_cpol:
                    add.append(f'\n  custom_policy_name = "{cpol_val}"')
                out = out[:insert_pos] + "".join(add) + out[insert_pos:]
    return out


# ---------------- Small list rendering helpers ----------------
def _line_indent_of(s: str, idx: int) -> int:
    line_start = s.rfind("\n", 0, idx) + 1
    n = 0
    while line_start + n < len(s) and s[line_start + n] == " ":
        n += 1
    return n

def _extract_quoted_items(inside: str) -> list[str]:
    return re.findall(r'"([^"]+)"', inside)

def _render_pretty_array(items: list[str], base_indent: int, items_indent: int = 2) -> str:
    head = " " * base_indent + "["
    pad  = " " * (base_indent + items_indent)
    tail = "\n" + " " * base_indent + "]"
    if not items:
        return head + tail
    body = "\n" + ",\n".join(f'{pad}"{v}"' for v in items)
    return head + body + tail


# ---------------- S3 TG patchers ----------------
def add_role_to_cmk_user_iam_arns_name(hcl_text: str, role_arn: str) -> str:
    """Append role_arn into cmk_user_iam_arns.name = [ ... ]"""
    scope_start = hcl_text.find("cmk_user_iam_arns")
    if scope_start < 0:
        return hcl_text
    scoped = hcl_text[scope_start:]
    m = re.search(r'name\s*=\s*\[', scoped)
    if not m:
        return hcl_text
    anchor_idx = scope_start + m.start()
    open_br = hcl_text.find("[", anchor_idx)
    if open_br < 0: return hcl_text
    close_br = hcl_text.find("]", open_br)
    if close_br < 0: return hcl_text
    inside = hcl_text[open_br + 1: close_br]
    items  = _extract_quoted_items(inside)
    if role_arn not in items:
        items.append(role_arn)
    base_indent = _line_indent_of(hcl_text, open_br + 1)
    pretty = _render_pretty_array(items, base_indent, 2)
    return hcl_text[:open_br] + pretty + hcl_text[close_br + 1:]


def add_role_to_allow_access_for_adgroups(hcl_text: str, role_arn: str) -> str:
    """Append role_arn to "AllowAccessForADGroups" -> Principal.AWS array (JSON inside jsonencode)."""
    sid_block = re.search(r'"Sid"\s*:\s*"AllowAccessForADGroups"[\s\S]*?}', hcl_text)
    if not sid_block:
        return hcl_text
    block_text = sid_block.group(0)
    m = re.search(r'"AWS"\s*:\s*\[([\s\S]*?)\]', block_text)
    if not m:
        return hcl_text
    start_in_block, end_in_block = m.start(1), m.end(1)
    inside = block_text[start_in_block:end_in_block]
    items  = _extract_quoted_items(inside)
    if role_arn not in items:
        items.append(role_arn)
    pretty = _render_pretty_array(items, 0, 2)
    new_block = block_text[:m.start()] + '"AWS" = ' + pretty + block_text[m.end():]
    return hcl_text[:sid_block.start()] + new_block + hcl_text[sid_block.end():]


def add_role_to_all_principal_arn_lists(hcl_text: str, role_arn: str) -> str:
    """Append role_arn to every "aws:PrincipalArn" = [ ... ] array (covers both Deny statements)."""
    pattern = re.compile(r'("aws:PrincipalArn"\s*=\s*)(\[\s*[\s\S]*?\s*\])')
    def repl(m: re.Match) -> str:
        header, arr = m.group(1), m.group(2)
        open_idx = arr.find("["); close_idx = arr.rfind("]")
        inside = arr[open_idx + 1: close_idx]
        items  = _extract_quoted_items(inside)
        if role_arn not in items:
            items.append(role_arn)
        pretty = _render_pretty_array(items, 0, 2)
        return header + pretty
    return pattern.sub(repl, hcl_text)


# ================== MAIN ==================
def lambda_handler(event, context):
    p = parse_payload(event)
    # Required inputs to form iam_name
    required = ["prefix", "environment", "app_name", "role", "stage"]
    for k in required:
        if k not in p or not str(p[k]).strip():
            return {"statusCode": 400, "body": json.dumps({"error": f"missing key: {k}", "required": required})}

    prefix = p["prefix"].strip()
    environment = p["environment"].strip()
    app = p["app_name"].strip()
    role = p["role"].strip()
    stage = p["stage"].strip()

    iam_name = f"{prefix}_{environment}-{app}_{role}-{stage}"
    dest_dir = f"{DEST_PARENT_DIR.strip('/')}/{iam_name}"
    role_name_value = f"{ROLE_ARN_PREFIX}{iam_name}"
    custom_policy_name = f"tbdpt-{iam_name}-rw-policy"

    api = f"https://api.github.com/repos/{GH_OWNER}/{GH_REPO}"

    # 1) Branch → commit
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

    # 5) Edit copied role terragrunt.hcl
    if src_tg_blob_sha:
        blob = gh("GET", f"{api}/git/blobs/{src_tg_blob_sha}", GITHUB_TOKEN)
        original_text = b64dec_utf8(blob["content"]) if blob.get("encoding") == "base64" else blob.get("content","")
        edited_text = update_role_tg(original_text, role_name_value, custom_policy_name)
        new_blob = gh("POST", f"{api}/git/blobs", GITHUB_TOKEN, {"content": edited_text, "encoding": "utf-8"})
        # override copied file with edited blob
        entries = [e for e in entries if e["path"] != dst_tg_fullpath]
        entries.append({"path": dst_tg_fullpath, "mode": "100644", "type": "blob", "sha": new_blob["sha"]})

    # 6) Edit S3 terragrunt.hcl with same role ARN
    try:
        s3_file = gh("GET", f"{api}/contents/{S3_TG_PATH}?ref={GH_BRANCH}", GITHUB_TOKEN)
        s3_text = b64dec_utf8(s3_file["content"])

        s3_text = add_role_to_cmk_user_iam_arns_name(s3_text, role_name_value)          # cmk_user_iam_arns.name
        s3_text = add_role_to_allow_access_for_adgroups(s3_text, role_name_value)       # AllowAccessForADGroups Principal.AWS
        s3_text = add_role_to_all_principal_arn_lists(s3_text, role_name_value)         # all "aws:PrincipalArn" arrays

        s3_blob = gh("POST", f"{api}/git/blobs", GITHUB_TOKEN, {"content": s3_text, "encoding": "utf-8"})
        entries.append({"path": S3_TG_PATH, "mode": "100644", "type": "blob", "sha": s3_blob["sha"]})
    except Exception as e:
        print(f"[S3 TG edit skipped] {e}")

    # 7) Create tree
    new_tree = gh("POST", f"{api}/git/trees", GITHUB_TOKEN, {"base_tree": base_tree_sha, "tree": entries})
    new_tree_sha = new_tree["sha"]

    # 8) Commit
    msg = f"{COMMIT_MSG} → {iam_name}"
    new_commit = gh("POST", f"{api}/git/commits", GITHUB_TOKEN, {
        "message": msg,
        "tree": new_tree_sha,
        "parents": [base_commit_sha],
        "author": {"name":"Lambda Bot","email":"lambda@example.com"},
        "committer":{"name":"Lambda Bot","email":"lambda@example.com"}
    })
    new_commit_sha = new_commit["sha"]

    # 9) Update ref
    gh("PATCH", f"{api}/git/refs/heads/{GH_BRANCH}", GITHUB_TOKEN, {"sha": new_commit_sha, "force": False})

    return {
        "statusCode": 200,
        "body": json.dumps({
            "iam_name": iam_name,
            "copied_from": SOURCE_DIR,
            "copied_to": dest_dir,
            "terragrunt_role_modified": bool(src_tg_blob_sha),
            "s3_tg_modified": True,
            "role_name": role_name_value,
            "custom_policy_name": custom_policy_name,
            "dest_role_tg_path": dst_tg_fullpath,
            "s3_tg_path": S3_TG_PATH,
            "commit_sha": new_commit_sha,
            "message": msg
        })
    }
