import os, sys
try:
    from github import Github
except ModuleNotFoundError:
    os.system("pip install PyGithub")
    from github import Github

ORG_NAME = 'Legacy-Framework'
TARGET_BRANCH = 'test-purposes' # 'test-workflow'
TOKEN = None

"""
        Don't bloody share your token !
        Reset it with 'insert_token' after testing
"""
# TOKEN = 'insert_token'

def update_readme(token):
    # Initialize GitHub client
    g = Github(token)

    # Get all repositories for the authenticated user
    org = g.get_organization(ORG_NAME)
    repos = org.get_repos()

    total_stars = 0
    total_commits = 0
    total_contributors = set()
    total_forks = 0

    for repo in repos:
        if repo.name == '.github':
            continue

        total_stars += repo.stargazers_count
        total_forks += repo.forks_count

        # Get commits and contributors
        contributors = repo.get_contributors()
        total_contributors.update(contributor.id for contributor in contributors)

        commits = repo.get_commits()
        total_commits += commits.totalCount

    # Read the README file
    readme_path = '.github/profile/README.md'
    with open(readme_path, 'r') as file:
        content = file.read()

    # Replace the STATS section
    new_stats = f"""
    <!-- STATS_START -->
    <p align="center">
        <img alt="Total Stars" src="https://img.shields.io/badge/Total_Stars-{total_stars}★-gold" />
        <img alt="Total Commits" src="https://img.shields.io/badge/Total_Commits-{total_commits}⇑-darkblue" />
        <img alt="Total Contributors" src="https://img.shields.io/badge/Total_Contributors-{len(total_contributors)}ጰ-blue" />
        <img alt="Total Forks" src="https://img.shields.io/badge/Total_Forks-{total_forks}↰↱-orange" />
    </p>
    <!-- STATS_END -->
    """

    updated_content = content.split('<!-- STATS_START -->')[0] + new_stats + content.split('<!-- STATS_END -->')[1]

    # Write the updated content back to the README file
    with open(readme_path, 'w') as file:
        file.write(updated_content)

if __name__ == "__main__":    
    print("\nSystem Arguments Valid?", len(sys.argv) < 2, "\nManual Token Override?", TOKEN is None, "\nValid Token?", (isinstance(TOKEN, str) and len(TOKEN) < 20),"\n")

    if len(sys.argv) < 2 ^ (TOKEN is None and (isinstance(TOKEN, str) and len(TOKEN) < 15)):
        print("\nError: Missing GITHUB_TOKEN argument\n")
        sys.exit(1)

    github_token = TOKEN or os.getenv('GITHUB_TOKEN') or sys.argv[1]
    update_readme(token=github_token)