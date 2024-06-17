import os, sys
from github import Github

ORG_NAME = 'Legacy-Framework'
TARGET_BRANCH = 'main'

def update_contributors(new_list: list, initial_list: list = []) -> list:
    for person in new_list:
        if not person in initial_list:
            initial_list.append(person)

    return initial_list

def update_readme(token:str=None):
    g = Github(token)
    org = g.get_organization(ORG_NAME)


    start_marker = '<!-- STATS_START -->'
    end_marker = '<!-- STATS_END -->'

    repo_stats = {
        "stars": 0,
        "commits": 0,
        "contributors": [],
        "forks": 0,
    }
    for repo in org.get_repos():
        repo_stats["stars"] += repo.stargazers_count
        repo_stats["commits"] += repo.get_commits().totalCount
        repo_stats["contributors"] = update_contributors(
            initial_list=repo_stats["contributors"],
            new_list=repo.get_contributors()
        )
        repo_stats["forks"] += repo.forks_count

    print("Total Statistics:")
    print(" - Stars", repo_stats["stars"])
    print(" - Commits", repo_stats["commits"])
    print(" - Contributors", len(repo_stats["contributors"]))
    print(" - Forks", repo_stats["forks"])

    updated_content = f"""
{start_marker}
<p align="center">
    <img alt="Total Stars" src="https://img.shields.io/badge/Stars-{repo_stats["stars"]}★-gold" />
    <img alt="Total Commits" src="https://img.shields.io/badge/Commits-{repo_stats["commits"]}-green" />
    <img alt="Total Contributors" src="https://img.shields.io/badge/Contributors-{len(repo_stats["contributors"])}ጰ-blue" />
    <img alt="Total Forks" src="https://img.shields.io/badge/Forks-{repo_stats["forks"]}↰↱-orange" />
</p>
{end_marker}
    """

    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    readme_path = os.path.join(parent_dir, 'profile/README.md')

    with open(readme_path, 'r') as file:
        readme = file.read().split("\n")

    markerState = False
    updated_readme = []
    for line in readme:
        if start_marker in line:
            markerState = True
            updated_readme.append(updated_content)
        elif end_marker in line:
            markerState = False
        elif not markerState:
            updated_readme.append(line)


    with open(readme_path, 'w') as file:
        file.write("\n".join(updated_readme))

    if token is not None:
        os.system('git config --global user.email "actions@github.com"')
        os.system('git config --global user.name "GitHub Actions"')
        os.system(f'git checkout {TARGET_BRANCH}')
        os.system(f'git add {readme_path}')
        os.system('git commit -m "Update README.md with latest stats"')
        os.system(f'git push origin {TARGET_BRANCH}')
    else:
        print('No Token was found for "GITHUB_TOKEN"')
        print('Keys:', os.environ.keys())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Missing GITHUB_TOKEN argument")
        sys.exit(1)

    github_token = sys.argv[1]
    update_readme(token=github_token)
