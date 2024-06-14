import requests
from datetime import datetime, timedelta


def get_recent_commits(repo_owner, repo_name, branch, token):
    """
    Fetches all commits from the last month to a specific branch in a GitHub repository.

    :param repo_owner: The owner of the repository
    :param repo_name: The name of the repository
    :param branch: The branch name
    :param token: Personal access token for GitHub API
    :return: List of recent commits
    """
    # Calculate the date one month ago
    since_date = (datetime.now() - timedelta(days=30)).isoformat()

    # GitHub API URL for commits
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits"

    # Headers for authentication
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Parameters for the API call
    params = {
        "sha": branch,
        "since": since_date
    }

    # Make the API request
    response = requests.get(url, headers=headers, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        commits = response.json()
        return commits
    else:
        # If there was an error, raise an exception
        response.raise_for_status()


# Example usage
if __name__ == "__main__":
    repo_owner = "example_owner"
    repo_name = "example_repo"
    branch = "main"
    token = "your_github_token"

    commits = get_recent_commits(repo_owner, repo_name, branch, token)
    for commit in commits:
        print(commit['commit']['message'])
