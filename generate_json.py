import os
import json
import requests

def get_file_commiters(owner, repo, file_path, token=None):
    base_url = "https://api.github.com"
    commits_url = f"{base_url}/repos/{owner}/{repo}/commits"
    commiters = set()

    headers = {
        "Accept": "application/vnd.github+json"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    page = 1
    while True:
        params = {
            "path": file_path,
            "page": page,
            "per_page": 100
        }
        response = requests.get(commits_url, headers=headers, params=params)
        response.raise_for_status()

        commit_data = response.json()
        if not commit_data:
            break

        for commit_obj in commit_data:
            author_info = commit_obj.get("author")
            if author_info and "login" in author_info:
                commiters.add(author_info["login"])

        page += 1

    return list(commiters)

def collect_rules(rules_folder="rules",
                  output_file="rules.json",
                  github_owner="stacklok",
                  github_repo="prompt-library",
                  github_token=os.environ.get("GITHUB_TOKEN")):
    """
    Iterates over each subfolder in 'rules', reads the .cursorrules file, and
    collects commiter info from GitHub if repo details are provided.
    Additionally, if a README.md file exists in the subfolder, a 'readme' field is added,
    containing a link to the README file on GitHub.
    """
    rules_data = []

    subfolders = [
        entry for entry in os.listdir(rules_folder)
        if os.path.isdir(os.path.join(rules_folder, entry))
    ]

    for subfolder in subfolders:
        print(f'processing "{subfolder}"')
        rule_dir = os.path.join(rules_folder, subfolder)
        cursorrules_path = os.path.join(rule_dir, ".cursorrules")
        
        if not os.path.exists(cursorrules_path):
            print(f"Warning: No .cursorrules file found in {subfolder} folder.")
            continue
        
        with open(cursorrules_path, "r", encoding="utf-8") as file:
            content = file.read()

        readme_file_path = os.path.join(rule_dir, "README.md")
        if os.path.exists(readme_file_path):
            readme_url = f"https://github.com/{github_owner}/{github_repo}/blob/main/{rules_folder}/{subfolder}/README.md"
        else:
            readme_url = None

        commiters = []
        if github_owner and github_repo:
            repo_file_path = os.path.join(rules_folder, subfolder, ".cursorrules")
            repo_file_path = repo_file_path.replace('\\', '/')
            commiters = get_file_commiters(github_owner, github_repo, repo_file_path, github_token)

        rules_data.append({
            "name": subfolder,
            "text": content,
            "commiters": commiters,
            "readme": readme_url
        })

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(rules_data, f, indent=2, ensure_ascii=False)

    print(f"Rules data collected and saved to {output_file}.")

if __name__ == "__main__":
    collect_rules()
