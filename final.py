# lambda_function.py
import json
import base64
import re
import urllib.request, urllib.error

# ================== HARDCODED CONFIG ==================
GITHUB_TOKEN = "88"
GH_OWNER     = "techdecipher"
GH_REPO      = "dummy"
GH_BRANCH    = "dev"              # e.g., "main" or "staging"

SOURCE_DIR   = "pnp-role-common"   # folder to copy from (relative to repo root)
DEST_DIR     = "pnp-role-common03"         # folder to copy to (hardcoded)

# terragrunt.hcl that lives inside the folder; we will override it at the destination
TG_FILE_BASENAME = "terragrunt.hcl"

# desired values to set in the copied terragrunt.hcl
ROLE_NAME_VALUE          = "tbdpt-persona-role"          # <— change me
CUSTOM_POLICY_NAME_VALUE = "tbdpt-persona-rw-policy"     # <— change me

COMMIT_MSG = f"copy {SOURCE_DIR} -> {DEST_DIR} and update terragrunt.hcl role/policy"
# ======================================================


# ------------- GitHub helper -------------
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
            txt = r.read().decode("utf-8")
            return json.loads(txt) if txt else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"GitHub {method} {url} -> {e.code}: {detail}")


# ------------- HCL edit helpers -------------
_role_pat   = re.compile(r'(?m)^\s*role_name\s*=\s*".*?"\s*$')
_cpol_pat   = re.compile(r'(?m)^\s*custom_policy_name\s*=\s*".*?"\s*$')
_inputs_pat = re.compile(r'(?s)inputs\s*=\s*{')

def update_terragrunt(text: str, role_val: str, cpol_val: str) -> str:
    """Update role_name and custom_policy_name in the inputs block.
       If keys are missing, insert them inside the inputs block."""
    updated = text

    # Replace if present
    found_role = bool(_role_pat.search(updated))
    found_cpol = bool(_cpol_pat.search(updated))

    if found_role:
        updated = _role_pat.sub(f'role_name = "{role_val}"', updated)
    if found_cpol:
        updated = _cpol_pat.sub(f'custom_policy_name = "{cpol_val}"', updated)

    # If either is missing, insert into inputs block
    if not (found_role and found_cpol):
        m = _inputs_pat.search(updated)
        if m:
            # find insert position right after the opening "{"
            # locate the "{" after "inputs ="
            brace_idx = updated.find("{", m.end() - 1)
            if brace_idx != -1:
                insert_pos = brace_idx + 1
                # prepare lines respecting indentation
                # determine indentation by peeking next line
                # fallback to 2 spaces
                indent = "  "
                # Build what to insert (only missing ones)
                lines_to_add = []
                if not found_role:
                    lines_to_add.append(f'\n{indent}role_name = "{role_val}"')
                if not found_cpol:
                    lines_to_add.append(f'\n{indent}custom_policy_name = "{cpol_val}"')
                updated = updated[:insert_pos] + "".join(lines_to_add) + updated[insert_pos:]
            # if inputs block not well-formed, we silently skip; we already did replacements if present
    return updated


# ------------- Base64 utils -------------
def b64dec_utf8(b64txt: str) -> str:
    return base64.b64decode(b64txt.replace("\n", "").encode()).decode("utf-8")


def lambda_handler(event, context):
    api = f"https://api.github.com/repos/{GH_OWNER}/{GH_REPO}"

    # 1) Get branch ref -> commit SHA
    ref = gh("GET", f"{api}/git/ref/heads/{GH_BRANCH}", GITHUB_TOKEN)
    base_commit_sha = ref["object"]["sha"]

    # 2) Get base commit -> tree SHA
    base_commit = gh("GET", f"{api}/git/commits/{base_commit_sha}", GITHUB_TOKEN)
    base_tree_sha = base_commit["tree"]["sha"]

    # 3) Get recursive tree
    tree = gh("GET", f"{api}/git/trees/{base_tree_sha}?recursive=1", GITHUB_TOKEN)
    if "tree" not in tree:
        return {"statusCode": 404, "body": json.dumps({"error": "Repo tree not found"})}

    src_prefix = SOURCE_DIR.strip("/") + "/"
    dst_prefix = DEST_DIR.strip("/") + "/"
    entries = []
    src_tg_blob_sha = None
    src_tg_fullpath = f"{SOURCE_DIR.strip('/')}/{TG_FILE_BASENAME}"
    dst_tg_fullpath = f"{DEST_DIR.strip('/')}/{TG_FILE_BASENAME}"

    # 4) Collect all file blobs under SOURCE_DIR; detect terragrunt.hcl blob SHA
    for node in tree["tree"]:
        if node.get("type") == "blob" and node.get("path", "").startswith(src_prefix):
            rel = node["path"][len(src_prefix):]
            new_path = f"{dst_prefix}{rel}"
            entries.append({
                "path": new_path,
                "mode": node.get("mode", "100644"),
                "type": "blob",
                "sha": node["sha"]
            })
            if node["path"] == src_tg_fullpath:
                src_tg_blob_sha = node["sha"]

    if not entries:
        return {"statusCode": 404, "body": json.dumps({"error": f"No files found under '{SOURCE_DIR}'"})}

    # 5) If terragrunt.hcl existed in source, fetch -> modify -> create new blob -> override destination path
    if src_tg_blob_sha:
        # Get blob content (base64) from Git Data API (not Contents API)
        blob = gh("GET", f"{api}/git/blobs/{src_tg_blob_sha}", GITHUB_TOKEN)
        if blob.get("encoding") == "base64":
            original_text = b64dec_utf8(blob.get("content", ""))
        else:
            # Rare; but handle utf-8 direct
            original_text = blob.get("content", "")

        edited_text = update_terragrunt(original_text, ROLE_NAME_VALUE, CUSTOM_POLICY_NAME_VALUE)

        # Create a new blob from edited text
        new_blob = gh("POST", f"{api}/git/blobs", GITHUB_TOKEN, {
            "content": edited_text,
            "encoding": "utf-8"
        })
        # Remove any earlier entry for the same destination path, then add our edited one
        entries = [e for e in entries if e["path"] != dst_tg_fullpath]
        entries.append({
            "path": dst_tg_fullpath,
            "mode": "100644",
            "type": "blob",
            "sha": new_blob["sha"]
        })
    # If the source didn’t have terragrunt.hcl, we just keep the copy as-is (nothing to edit).

    # 6) Create new tree using base_tree + our entries
    new_tree = gh("POST", f"{api}/git/trees", GITHUB_TOKEN, {
        "base_tree": base_tree_sha,
        "tree": entries
    })
    new_tree_sha = new_tree["sha"]

    # 7) Create commit
    new_commit = gh("POST", f"{api}/git/commits", GITHUB_TOKEN, {
        "message": COMMIT_MSG,
        "tree": new_tree_sha,
        "parents": [base_commit_sha],
        "author":   {"name": "Lambda Bot", "email": "lambda@example.com"},
        "committer":{"name": "Lambda Bot", "email": "lambda@example.com"}
    })
    new_commit_sha = new_commit["sha"]

    # 8) Update branch
    gh("PATCH", f"{api}/git/refs/heads/{GH_BRANCH}", GITHUB_TOKEN, {
        "sha": new_commit_sha,
        "force": False
    })

    return {
        "statusCode": 200,
        "body": json.dumps({
            "copied_from": SOURCE_DIR,
            "copied_to": DEST_DIR,
            "terragrunt_modified": bool(src_tg_blob_sha),
            "role_name": ROLE_NAME_VALUE,
            "custom_policy_name": CUSTOM_POLICY_NAME_VALUE,
            "dest_terragrunt_path": dst_tg_fullpath,
            "commit_sha": new_commit_sha,
            "message": COMMIT_MSG
        })
    }
