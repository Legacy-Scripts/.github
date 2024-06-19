import os, sys

try:
    import github
    from github import Github
except ModuleNotFoundError:
    os.system("pip install PyGithub")
    import github
    from github import Github

ORG_NAME = 'Legacy-Framework'
TARGET_BRANCH = 'test-workflow' # 'main'
TOKEN = None # Don't remove this line

"""
        Don't bloody share your token !
        Reset it with 'insert_token' after testing
"""
# TOKEN = 'insert_token'

def update_contributors(new_list: list, initial_list: list = []) -> list:
    for person in new_list:
        if not person in initial_list:
            initial_list.append(person)

    return initial_list

def update_readme(token:str=None):
    g = Github(token)
    try:
        org = g.get_organization(ORG_NAME)
    except github.GithubException.BadCredentialsException:
        g = Github(os.getenv('GITHUB_TOKEN'))
        org = g.get_organization(ORG_NAME)
    
    # os.system('git config --global user.email "actions@github.com"')
    # os.system('git config --global user.name "GitHub Actions"')
    # os.system('git fetch')
    # os.system(f'git checkout {TARGET_BRANCH}')

    start_marker = '<!-- STATS_START -->'
    end_marker = '<!-- STATS_END -->'

    repo_stats = {
        "stars": 0,
        "commits": 0,
        "contributors": [],
        "forks": 0,
    }
    for repo in org.get_repos():
        if not '.github' in repo.full_name:
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
    <img alt="Total Stars" src="https://img.shields.io/badge/Total_Stars-{repo_stats["stars"]}★-gold" />
    <img alt="Total Commits" src="https://img.shields.io/badge/Total_Commits-{repo_stats["commits"]}⇑-darkblue" />
    <img alt="Total Contributors" src="https://img.shields.io/badge/Total_Contributors-{len(repo_stats["contributors"])}ጰ-blue" />
    <img alt="Total Forks" src="https://img.shields.io/badge/Total_Forks-{repo_stats["forks"]}↰↱-orange" />
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

    print("Wrinting to file {}".format(readme_path))
    with open(readme_path, 'w') as file:
        file.write("\n".join(updated_readme))

    """ Commitingh g hangjeb """
    # print("\n     Adding File")
    # os.system(f'git add {readme_path}')
    # print("\n     Commiting File")
    # os.system('git commit -m "chore: update README stats"')
    # print("\n     Pushing Changes")
    # os.system(f'git push origin {TARGET_BRANCH}')

if __name__ == "__main__":

    print("\nSystem Arguments Valid?", len(sys.argv) > 1, "\nManual Token Override?", TOKEN is not None, "\nValid Token?", (isinstance(TOKEN, str) and len(TOKEN) > 35),"\n")

    if len(sys.argv) < 2 and (TOKEN is None or (isinstance(TOKEN, str) and len(TOKEN) < 35)):
        print("\nError: Missing GITHUB_TOKEN argument\n")
        sys.exit(1)

    github_token = TOKEN or sys.argv[1]
    update_readme(token=github_token)
