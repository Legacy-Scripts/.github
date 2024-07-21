import os
import sys
import urllib.parse

try:
    from github import Github, Auth
except ModuleNotFoundError:
    os.system("pip install PyGithub")
    from github import Github, Auth

ORG_NAME = 'Legacy-Framework'
TARGET_BRANCH = 'main'  # 'test-workflow'
TOKEN = None

"""
        Don't bloody share your token !
        Reset it with 'insert_token' after testing
"""
# TOKEN = 'insert_token'

def generate_pie_chart_url(language_counts):
    labels = list(language_counts.keys())
    data = list(language_counts.values())
    
    # Create the pie chart JSON configuration
    chart_config = {
        "type": "pie",
        "data": {
            "labels": labels,
            "datasets": [{
                "data": data
            }]
        }
    }
    
    # Convert the configuration to a JSON string and then URL-encode it
    chart_config_json = urllib.parse.quote(str(chart_config).replace("'", '"'))
    
    # Create the pie chart URL
    chart_url = f"https://quickchart.io/chart?c={chart_config_json}"
    return chart_url

def update_readme(token):
    # Initialize GitHub client
    g = Github(auth=Auth.Token(token))

    # Get all repositories for the authenticated user
    org = g.get_organization(ORG_NAME)

    total_stars = 0
    total_commits = 0
    total_contributors = set()
    total_forks = 0
    language_counts = {}

    for repo in org.get_repos(type='all'):
        print(f"Processing repository: {repo.name} (Private: {repo.private})")
        if repo.name == '.github':
            continue

        total_stars += repo.stargazers_count
        total_forks += repo.forks_count

        # Get commits and contributors
        contributors = repo.get_contributors()
        total_contributors.update(contributor.id for contributor in contributors)

        commits = repo.get_commits()
        total_commits += commits.totalCount

        # Get primary language
        language = repo.language
        if language:
            if language in language_counts:
                language_counts[language] += 1
            else:
                language_counts[language] = 1

    print("\nRecap")
    print("total_stars", total_stars)
    print("total_commits", total_commits)
    print("total_contributors", total_contributors)
    print("total_forks", total_forks)
    print("language_counts", language_counts)
    print("\n")

    # Read the README file
    readme_path = 'profile/README.md'
    with open(readme_path, 'r') as file:
        content = file.read()

    # Generate pie chart URL
    pie_chart_url = generate_pie_chart_url(language_counts)

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

    # <br/>
    # <img alt="Language Pie Chart" src="{pie_chart_url}" />

    updated_content = content.split('<!-- STATS_START -->')[0] + new_stats[1:] + content.split('<!-- STATS_END -->')[1]

    # Write the updated content back to the README file
    with open(readme_path, 'w') as file:
        file.write(updated_content)

if __name__ == "__main__":
    print("\nSystem Arguments Valid?", len(sys.argv) < 2, "\nManual Token Override?", TOKEN is None, "\nValid Token?", (isinstance(TOKEN, str) and len(TOKEN) < 20), "\n")

    if TOKEN is None or len(TOKEN) < 15:
        TOKEN = os.getenv('GITHUB_TOKEN')

    if not (len(sys.argv) < 2 ^ (TOKEN is None and (isinstance(TOKEN, str) and len(TOKEN) < 15))):
        print("\nError: Missing GITHUB_TOKEN argument\n")
        sys.exit(1)

    github_token = TOKEN or os.getenv('GITHUB_TOKEN') or sys.argv[1]
    update_readme(token=github_token)
