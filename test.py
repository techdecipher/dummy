import os
import json
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
import requests

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

def run(cmd, cwd=None):
    subprocess.run(cmd, cwd=cwd, check=True, stdout=subprocess.DEVNULL)

# ---------- GitHub helpers ----------

def get_team_id():
    url = f"https://api.github.com/orgs/{ORG_NAME}/teams/{DEFAULT_TEAM}"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json()["id"]

def create_repo(repo_name, team_id):
    url = f"https://api.github.com/orgs/{ORG_NAME}/repos"
    payload = {
        "name": repo_name,
        "private": True,
        "team_id": team_id
    }
    r = requests.post(url, headers=HEADERS, json=payload)
    if r.status_code not in (201, 422):  # 422 = already exists
        r.raise_for_status()

def create_pr(repo, base, head, title, body):
    url = f"https://api.github.com/repos/{ORG_NAME}/{repo}/pulls"
    r = requests.post(
        url,
        headers=HEADERS,
        json={
            "title": title,
            "head": head,
            "base": base,
            "body": body
        }
    )
    r.raise_for_status()
    return r.json()["html_url"]

# ---------- Core Logic ----------

def lambda_handler(event, context):
    pod = event["pod_name"].lower()
    repo_name = f"tdspin-tf-{pod}-pod-infra"

    team_id = get_team_id()
    create_repo(repo_name, team_id)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        # Clone central chofer repo
        chofer_url = f"https://{GITHUB_TOKEN}@github.com/{ORG_NAME}/{CHOFER_REPO}.git"
        run(["git", "clone", "-b", CHOFER_BRANCH, chofer_url, "."], cwd=tmp)

        # Create branch
        branch = f"podonboard/{pod}"
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

        # Commit & push
        run(["git", "add", "."], cwd=tmp)
        run(
            ["git", "commit", "-m", f"Onboard {pod} repo"],
            cwd=tmp
        )
        run(["git", "push", "-u", "origin", branch], cwd=tmp)

    pr_url = create_pr(
        CHOFER_REPO,
        CHOFER_BRANCH,
        branch,
        f"Onboard {pod}",
        f"Automated onboarding for {pod}"
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "repo_created": repo_name,
            "pr_url": pr_url
        })
    }