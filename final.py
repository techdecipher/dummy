# lambda_function.py
import json
import urllib.request, urllib.error

# ======= HARDCODED CONFIG =======
GITHUB_TOKEN = "888"
GH_OWNER     = "techdecipher"
GH_REPO      = "dummy"
GH_BRANCH    = "dev"
SOURCE_DIR   = "pnp-role-common"     # Folder to copy
DEST_DIR     = "pnp-role-common02"  # Destination folder
# =================================

def gh(method, url, token, body=None):
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "lambda-folder-copy")
    if body is not None:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(body).encode("utf-8")
    try:
        with urllib.request.urlopen(req) as r:
            txt = r.read().decode("utf-8")
            return json.loads(txt) if txt else {}
    except urllib.error.HTTPError as e:
        print(e.read().decode("utf-8", errors="ignore"))
        raise

def lambda_handler(event, context):
    api = f"https://api.github.com/repos/{GH_OWNER}/{GH_REPO}"

    # 1) Get branch reference
    ref = gh("GET", f"{api}/git/ref/heads/{GH_BRANCH}", GITHUB_TOKEN)
    base_commit_sha = ref["object"]["sha"]

    # 2) Get base commit → tree
    commit = gh("GET", f"{api}/git/commits/{base_commit_sha}", GITHUB_TOKEN)
    base_tree_sha = commit["tree"]["sha"]

    # 3) Get recursive tree and find all files under source folder
    tree = gh("GET", f"{api}/git/trees/{base_tree_sha}?recursive=1", GITHUB_TOKEN)
    prefix = SOURCE_DIR.strip("/") + "/"
    entries = []
    for node in tree.get("tree", []):
        if node.get("type") == "blob" and node.get("path", "").startswith(prefix):
            rel = node["path"][len(prefix):]
            new_path = f"{DEST_DIR.strip('/')}/{rel}"
            entries.append({
                "path": new_path,
                "mode": node.get("mode", "100644"),
                "type": "blob",
                "sha": node["sha"]
            })

    if not entries:
        return {"statusCode": 404, "body": json.dumps({"error": f"No files found in {SOURCE_DIR}"})}

    # 4) Create new tree
    new_tree = gh("POST", f"{api}/git/trees", GITHUB_TOKEN, {
        "base_tree": base_tree_sha,
        "tree": entries
    })
    new_tree_sha = new_tree["sha"]

    # 5) Create commit
    commit_msg = f"Copied '{SOURCE_DIR}' to '{DEST_DIR}'"
    new_commit = gh("POST", f"{api}/git/commits", GITHUB_TOKEN, {
        "message": commit_msg,
        "tree": new_tree_sha,
        "parents": [base_commit_sha],
        "author": {"name": "Lambda Bot", "email": "lambda@example.com"},
        "committer": {"name": "Lambda Bot", "email": "lambda@example.com"}
    })
    new_commit_sha = new_commit["sha"]

    # 6) Update branch
    gh("PATCH", f"{api}/git/refs/heads/{GH_BRANCH}", GITHUB_TOKEN, {
        "sha": new_commit_sha,
        "force": False
    })

    return {
        "statusCode": 200,
        "body": json.dumps({
            "source": SOURCE_DIR,
            "destination": DEST_DIR,
            "commit_sha": new_commit_sha,
            "message": commit_msg
        })
    }
