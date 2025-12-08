import os
import json
import subprocess
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

# ================= ENV CONFIG =================

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
ORG_NAME = os.environ["ORG_NAME"]
DEFAULT_TEAM = os.environ["DEFAULT_TEAM"]
CHOFER_REPO = os.environ["CHOFER_REPO"]
CHOFER_BRANCH = os.environ.get("CHOFER_BRANCH", "master")
GHA_CONFIG_PATH = os.environ["GHA_CONFIG_PATH"]
TEAM_MAPPING_PATH = os.environ["TEAM_MAPPING_PATH"]

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# ================= UTIL =================

def run(cmd: list[str], cwd: Path | None = None):
    subprocess.run(
        cmd,
        cwd=cwd,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def github_request(method: str, url: str, body: dict | None = None):
    data = json.dumps(body).encode() if body else None
    headers = HEADERS | {"Content-Type": "application/json"}

    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=10) as res:
            return json.loads(res.read().decode())
    except HTTPError as e:
        if e.code == 422:  # repo already exists
            return {"status": "exists"}
        raise RuntimeError(f"GitHub API error {e.code}: {e.read().decode()}")

# ================= GITHUB OPS =================

def get_team_id() -> int:
    data = github_request(
        "GET",
        f"https://api.github.com/orgs/{ORG_NAME}/teams/{DEFAULT_TEAM}"
    )
    return data["id"]

def create_repo(repo_name: str, team_id: int):
    github_request(
        "POST",
        f"https://api.github.com/orgs/{ORG_NAME}/repos",
        {
            "name": repo_name,
            "private": True,
            "team_id": team_id
        }
    )

def create_pull_request(repo: str, head: str, base: str, title: str, body: str) -> str:
    data = github_request(
        "POST",
        f"https://api.github.com/repos/{ORG_NAME}/{repo}/pulls",
        {
            "title": title,
            "head": head,
            "base": base,
            "body": body
        }
    )
    return data["html_url"]

# ================= LAMBDA =================

def lambda_handler(event, context):
    """
    Payload:
    {
      "pod_name": "payments"
    }
    """

    pod = event["pod_name"].strip().lower()
    repo_name = f"tdspin-tf-{pod}-pod-infra"
    branch = f"podonboard/{pod}"

    # 1️⃣ Create repo under team
    team_id = get_team_id()
    create_repo(repo_name, team_id)

    # 2️⃣ Update central Chofer repo
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        chofer_url = (
            f"https://{GITHUB_TOKEN}@github.com/"
            f"{ORG_NAME}/{CHOFER_REPO}.git"
        )

        run(["git", "clone", "-b", CHOFER_BRANCH, chofer_url, "."], cwd=tmp)
        run(["git", "checkout", "-b", branch], cwd=tmp)

        # Append GHA config
        gha_file = tmp / GHA_CONFIG_PATH
        gha_file.write_text(
            gha_file.read_text() +
            f"\n{repo_name}:\n  cd_name: cd-terraform-standalone\n"
        )

        # Append team mapping
        team_file = tmp / TEAM_MAPPING_PATH
        team_file.write_text(
            team_file.read_text() +
            f"\n{repo_name}: {DEFAULT_TEAM}\n"
        )

        run(["git", "add", "."], cwd=tmp)
        run(["git", "commit", "-m", f"Onboard {pod} pod"], cwd=tmp)
        run(["git", "push", "-u", "origin", branch], cwd=tmp)

    # 3️⃣ Raise PR
    pr_url = create_pull_request(
        repo=CHOFER_REPO,
        head=branch,
        base=CHOFER_BRANCH,
        title=f"Onboard {pod} pod repo",
        body=f"Automated onboarding for pod {pod}"
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "repo_created": repo_name,
            "chofer_pr": pr_url
        })
    }