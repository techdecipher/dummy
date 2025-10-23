# lambda_function.py
import json, re, base64, urllib.request, urllib.error

# ======= HARDCODED CONFIG =======
GITHUB_TOKEN = "ghp_your_pat_here"
GH_OWNER     = "your-org-or-user"
GH_REPO      = "your-repo"
GH_BRANCH    = "staging"                 # or "main"
SOURCE_DIR   = "templates/base-app"      # folder to copy from
DEST_DIR     = "apps/persona"            # folder to copy to
FILE_PATH    = "scratch/terragrunt.hcl"  # file to modify with role edits
ROLE_ARN     = "arn:aws:iam::123456789012:role/tbdp_bucket02"
BUCKET_NAME  = "tbdp_bucket02"
COMMIT_MSG   = "scaffold app + policy role updates"
# =================================

# ------------ GitHub helper ------------
def gh(method, url, token, body=None):
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "lambda-gh-folder-copy-and-edit")
    if body is not None:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(body).encode("utf-8")
    try:
        with urllib.request.urlopen(req) as r:
            txt = r.read().decode("utf-8")
            return json.loads(txt) if txt else {}
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"GitHub {method} {url} -> {e.code}: {e.read().decode('utf-8', 'ignore')}")

# ------------ Base64 utils -------------
def b64dec_utf8(b64txt):
    return base64.b64decode(b64txt.replace("\n", "").encode()).decode("utf-8")

# ------------ Text helpers -------------
def line_indent_of(s, idx):
    line_start = s.rfind("\n", 0, idx) + 1
    i, n = line_start, 0
    while i < len(s) and s[i] == " ":
        i += 1; n += 1
    return n

def extract_quoted_items(inside):
    return re.findall(r'"([^"]+)"', inside)

def render_pretty_array(items, base_indent, items_indent):
    head = " " * base_indent + "["
    item_pad = " " * (base_indent + items_indent)
    tail = "\n" + " " * base_indent + "]"
    if not items: return head + tail
    body = "\n" + ",\n".join(f'{item_pad}"{v}"' for v in items)
    return head + body + tail

# ======== 1) cmk_user_iam_arns.name ========
def add_role_to_cmk_user_iam_arns(full_text, arn, items_indent=2):
    scope_start = full_text.find("cmk_user_iam_arns")
    if scope_start < 0:
        return add_arn_array_js_parity(full_text, r"name\s*=\s*\[", arn, items_indent)
    scoped = full_text[scope_start:]
    m = re.search(r"name\s*=\s*\[", scoped)
    if not m: return full_text
    anchor_idx = scope_start + m.start()
    after_anchor = full_text[anchor_idx:]
    open_idx = after_anchor.find("[")
    if open_idx < 0: return full_text
    start = anchor_idx + open_idx + 1
    end   = full_text.find("]", start)
    if end < 0: return full_text
    inside = full_text[start:end]
    items = extract_quoted_items(inside)
    if arn not in items: items.append(arn)
    base_indent = line_indent_of(full_text, start)
    pretty = render_pretty_array(items, base_indent, items_indent)
    return full_text[:start-1] + pretty + full_text[end+1:]

def add_arn_array_js_parity(full_text, anchor_regex, arn, items_indent=2):
    m = re.search(anchor_regex, full_text)
    if not m: return full_text
    anchor_idx = m.start()
    after_anchor = full_text[anchor_idx:]
    open_idx = after_anchor.find("[")
    if open_idx < 0: return full_text
    start = anchor_idx + open_idx + 1
    end   = full_text.find("]", start)
    if end < 0: return full_text
    inside = full_text[start:end]
    items = extract_quoted_items(inside)
    if arn not in items: items.append(arn)
    base_indent = line_indent_of(full_text, start)
    pretty = render_pretty_array(items, base_indent, items_indent)
    return full_text[:start-1] + pretty + full_text[end+1:]

# ======== 2) aws:PrincipalArn lists ========
def add_arn_to_all_principal_arn_lists(full_text, arn, items_indent=2):
    pattern = re.compile(r'("aws:PrincipalArn"\s*=\s*)(\[\s*[\s\S]*?\s*\])')
    def repl(match):
        array_block = match.group(2)
        start_br = array_block.find("[")
        end_br = array_block.rfind("]")
        inside = array_block[start_br + 1 : end_br]
        items = extract_quoted_items(inside)
        if arn not in items: items.append(arn)
        header = '"aws:PrincipalArn" = '
        pretty = render_pretty_array(items, 0, items_indent)
        return header + pretty
    return pattern.sub(repl, full_text)

# ======== 3) ProjectAccess block ========
def ensure_project_access_for_role(full_text, role_arn, bucket_name):
    block_re = re.compile(
        r'{[\s\S]*?Sid\s*=\s*"ProjectAccess"[\s\S]*?Principal\s*=\s*{\s*AWS\s*=\s*"([^"]+)"\s*}[\s\S]*?Action\s*=\s*\[[^\]]*?\][\s\S]*?Resource\s*=\s*"arn:aws:s3:::[^"]+"\s*}',
        re.MULTILINE
    )
    has_for_role = False
    def replace_block(block):
        nonlocal has_for_role
        m = re.search(r'Principal\s*=\s*{\s*AWS\s*=\s*"([^"]+)"', block)
        principal_arn = m.group(1) if m else None
        if principal_arn == role_arn:
            has_for_role = True
            return block
        if principal_arn and principal_arn.endswith(":role/ProjectDevRole"):
            has_for_role = True
            return re.sub(
                r'Principal\s*=\s*{\s*AWS\s*=\s*"([^"]+)"\s*}',
                f'Principal = {{ AWS = "{role_arn}" }}',
                block
            )
        return block
    replaced_text = block_re.sub(lambda m: replace_block(m.group(0)), full_text)
    if has_for_role:
        return replaced_text
    # Append new block into Statement = [ ... ]
    stmt_start = replaced_text.find("Statement = [")
    if stmt_start < 0: return replaced_text
    close_idx = replaced_text.find("\n    ]", stmt_start)
    if close_idx < 0: return replaced_text
    insert_pos = close_idx
    block = f"""
      ,{{
        Sid       = "ProjectAccess"
        Effect    = "Allow"
        Principal = {{ AWS = "{role_arn}" }}
        Action    = ["s3:ListBucket"]
        Resource  = "arn:aws:s3:::{bucket_name}"
      }}"""
    return replaced_text[:insert_pos] + block + replaced_text[insert_pos:]

# --------------- Main handler ---------------
def lambda_handler(event, context):
    api = f"https://api.github.com/repos/{GH_OWNER}/{GH_REPO}"

    # A) read branch → base commit
    ref = gh("GET", f"{api}/git/ref/heads/{GH_BRANCH}", GITHUB_TOKEN)
    base_commit_sha = ref["object"]["sha"]

    # B) base commit → base tree
    base_commit = gh("GET", f"{api}/git/commits/{base_commit_sha}", GITHUB_TOKEN)
    base_tree_sha = base_commit["tree"]["sha"]

    # C) get full tree to collect blobs for folder copy
    repo_tree = gh("GET", f"{api}/git/trees/{base_tree_sha}?recursive=1", GITHUB_TOKEN)

    entries = []
    prefix = SOURCE_DIR.strip("/") + "/"
    for node in repo_tree.get("tree", []):
        if node.get("type") == "blob" and node.get("path","").startswith(prefix):
            rel = node["path"][len(prefix):]
            entries.append({
                "path": f"{DEST_DIR.strip('/')}/{rel}",
                "mode": node.get("mode","100644"),
                "type": "blob",
                "sha": node["sha"]  # reuse blob
            })

    # D) fetch + modify policy file content
    try:
        file_obj = gh("GET", f"{api}/contents/{FILE_PATH}?ref={GH_BRANCH}", GITHUB_TOKEN)
        original_text = b64dec_utf8(file_obj["content"])
        edited_text = original_text
        edited_text = add_role_to_cmk_user_iam_arns(edited_text, ROLE_ARN, 2)
        edited_text = add_arn_to_all_principal_arn_lists(edited_text, ROLE_ARN, 2)
        edited_text = ensure_project_access_for_role(edited_text, ROLE_ARN, BUCKET_NAME)

        # create a new blob with edited content (utf-8)
        new_blob = gh("POST", f"{api}/git/blobs", GITHUB_TOKEN, {
            "content": edited_text,
            "encoding": "utf-8"
        })
        entries.append({
            "path": FILE_PATH,
            "mode": "100644",
            "type": "blob",
            "sha": new_blob["sha"]
        })
    except Exception as e:
        # If file isn’t found, proceed with just folder copy
        print(f"Policy edit skipped: {e}")

    if not entries:
        return {"statusCode": 404, "body": json.dumps({"error": "Nothing to commit (no files found / edits skipped)"})}

    # E) create new tree
    new_tree = gh("POST", f"{api}/git/trees", GITHUB_TOKEN, {
        "base_tree": base_tree_sha,
        "tree": entries
    })
    new_tree_sha = new_tree["sha"]

    # F) create commit
    new_commit = gh("POST", f"{api}/git/commits", GITHUB_TOKEN, {
        "message": COMMIT_MSG,
        "tree": new_tree_sha,
        "parents": [base_commit_sha],
        "author":   {"name": "Lambda Bot", "email": "lambda@example.com"},
        "committer":{"name": "Lambda Bot", "email": "lambda@example.com"}
    })
    new_commit_sha = new_commit["sha"]

    # G) move branch ref
    gh("PATCH", f"{api}/git/refs/heads/{GH_BRANCH}", GITHUB_TOKEN, {
        "sha": new_commit_sha,
        "force": False
    })

    return {
        "statusCode": 200,
        "body": json.dumps({
            "copied_from": SOURCE_DIR,
            "copied_to": DEST_DIR,
            "edited_file": FILE_PATH,
            "commit_sha": new_commit_sha,
            "message": COMMIT_MSG
        })
    }
