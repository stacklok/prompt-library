import os
import json
import requests

def get_file_contributors(owner, repo, file_path, token=None):
    base_url = "https://api.github.com"
    commits_url = f"{base_url}/repos/{owner}/{repo}/commits"
    contributors = set()

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
                contributors.add(author_info["login"])

        page += 1

    return list(contributors)

def collect_rules(rules_folder="rules",
                  output_file="rules_output.json",
                  github_owner="PatrickJS",
                  github_repo="awesome-cursorrules",
                  github_token=os.environ.get("GITHUB_TOKEN")):
    """
    Iterates over each subfolder in 'rules', reads the .cursorrules file, and
    collects contributor info from GitHub if repo details are provided.
    """
    rules_data = []

    subfolders = [
        entry for entry in os.listdir(rules_folder)
        if os.path.isdir(os.path.join(rules_folder, entry))
    ]

    for subfolder in subfolders:
        print(f'processing "{subfolder}"')
        cursorrules_path = os.path.join(rules_folder, subfolder, ".cursorrules")
        
        if not os.path.exists(cursorrules_path):
            print(f"Warning: No .cursorrules file found in {subfolder} folder.")
            continue
        
        with open(cursorrules_path, "r", encoding="utf-8") as file:
            content = file.read()

        contributors = []

        if github_owner and github_repo:
            repo_file_path = os.path.join(rules_folder, subfolder, ".cursorrules")
            repo_file_path = repo_file_path.replace('\\', '/')
            
            contributors = get_file_contributors(github_owner, github_repo, repo_file_path, github_token)

        rules_data.append({
            "name": subfolder,
            "text": content,
            "contributors": contributors
        })

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(rules_data, f, indent=2, ensure_ascii=False)

    print(f"Rules data collected and saved to {output_file}.")

if __name__ == "__main__":
    collect_rules()
