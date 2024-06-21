import requests
from datetime import datetime, timedelta
import pandas as pd

# Set Up
org = 'cat-digital-platform'
repo_name = 'A-ECRM-Master'
branch = 'ECRM_Devint'
pat = 'pat'


# Functino to get detailed information on Recent Commits
def get_recent_commits(org, repo_name, branch, pat):
    """
    Fetches all commits from the last month to a specific branch in a GitHub repository.

    :param org: The owner of the repository
    :param repo_name: The name of the repository
    :param branch: The branch name
    :param pat: Personal access pat for GitHub API
    :return: List of recent commits
    """
    # Calculate the date one month ago
    since_date = (datetime.now() - timedelta(days=30)).isoformat()
    # print(since_date)

    # GitHub API URL for commits
    url = f"https://api.github.com/repos/{org}/{repo_name}/commits"
    url2 = f"https://api.github.com/repos/{org}/{repo_name}/commits/{branch}"

    # Headers for authentication
    headers = {
        "Authorization": f"token {pat}",
        "Accept": "application/vnd.github+json"
    }

    # Parameters for the API call
    params = {
        "sha": branch,
        "since": since_date,
        "per_page": 100  # Maximum number of items per page
    }

    all_commits = []
    page = 1

    while True:
        # Update the page parameter for pagination
        params['page'] = page

        # Make the API request
        response = requests.get(url, headers=headers, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            commits = response.json()
            if not commits:
                # If no more commits are returned, break the loop
                break
            else:
                all_commits.extend(commits)
                page += 1
        else:
            # If there was an error, raise an exception
            print(f"Failed to retrieve commits from {branch} in {repo_name}.")
            response.raise_for_status()

    return all_commits


def convert_iso_to_date(iso_string: str) -> str:
    date_obj = datetime.fromisoformat(iso_string)

    # Desired format string
    desired_format = "%m-%d-%Y"

    # Convert datetime object to desired format
    formatted_string = date_obj.strftime(desired_format)

    return formatted_string


commit_messages_list = []
# employee_ID = []
employee_name = []
employee_email = []
commit_date = []

commits = get_recent_commits(org, repo_name, branch, pat)
for commit in commits:
    # print('_____________________________________________________________________________')
    # print(commit['commit']['message'])
    commit_messages_list.append(commit['commit']['message'])
    # print(commit['author']['id'])
    # employee_ID.append(commit['author']['id'])
    # print(commit['commit']['author'])
    employee_name.append(commit['commit']['author']['name'])
    employee_email.append(commit['commit']['author']['email'])

    date = convert_iso_to_date(commit['commit']['author']['date'])
    commit_date.append(date)
    # print(commit['commit']['author']['date'])


data = {
    "Commit Message": commit_messages_list,
    # "Employee ID": employee_ID,
    "Employee Name": employee_name,
    "Employee Email": employee_email,
    "Date": commit_date
}

df = pd.DataFrame(data)
df.to_csv("output.csv", index=False)

print("Done.")
