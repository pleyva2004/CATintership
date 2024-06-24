import requests
from datetime import datetime, timedelta
import pandas as pd

# Set Up
org = 'cat-digital-platform'
repo = 'A-ECRM-Master'
branch = 'ECRM_Devint'
pat = 'pat'


# Functino to get detailed information on Recent Commits
def get_recent_commits():
    """
    Fetches all commits from the last month to a specific branch in a GitHub repository.

    :param org: The owner of the repository
    :param repo: The name of the repository
    :param branch: The branch name
    :param pat: Personal access pat for GitHub API
    :return: List of recent commits
    """

    # Calculate the date one month ago
    since_date = (datetime.now() - timedelta(days=30)).isoformat()
    # print(since_date)

    # GitHub API URL for commits
    url = f"https://api.github.com/repos/{org}/{repo}/commits"
    url2 = f"https://api.github.com/repos/{org}/{repo}/commits/{branch}"

    # Headers for authentication
    headers = {
        "Authorization": f"Bearer {pat}",
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
            temp_commit = response.json()
            if not temp_commit:
                # If no more commits are returned, break the loop
                break
            else:
                all_commits.extend(temp_commit)
                page += 1
        else:
            # If there was an error, raise an exception
            print(f"Failed to retrieve commits from {branch} in {repo}.")
            response.raise_for_status()

    return all_commits


def get_pull_requests():

    url = f"https://api.github.com/repos/{org}/{repo}/pulls"
    headers = {"Authorization": f"token {pat}"}
    response = requests.get(url, headers=headers, params={"state": "all"})

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch pull requests: {response.status_code}")
        return None


def get_reviews(pull_number):
    url = f"https://api.github.com/repos/{org}/{repo}/pulls/{pull_number}/reviews"
    headers = {"Authorization": f"token {pat}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch reviews for pull request {pull_number}: {response.status_code}")
        return None


def convert_iso_to_date(iso_string: str) -> str:
    date_obj = datetime.fromisoformat(iso_string)

    # Desired format string
    desired_format = "%m-%d-%Y"

    # Convert datetime object to desired format
    formatted_string = date_obj.strftime(desired_format)

    return formatted_string


commit_messages_list = []
employee_name = []
employee_email = []
commit_date = []
approved_users = []


commits = get_recent_commits()
pull_requests = get_pull_requests()

for commit in commits:
    commit_messages_list.append(commit['commit']['message'])
    employee_name.append(commit['commit']['author']['name'])
    employee_email.append(commit['commit']['author']['email'])

    date = convert_iso_to_date(commit['commit']['author']['date'])
    commit_date.append(date)

    approved_users.append("")
    commit_sha = commit['sha']
    # Find the pull request associated with the commit
    for pr in pull_requests:
        if pr["merge_commit_sha"] == commit_sha:
            reviews = get_reviews(pr["number"])
            if reviews:
                print(f"Approvals for {commit_messages_list[-1]} :")
                for review in reviews:
                    print(review['user']['login'])
                    approved_users.pop()
                    approved_users.append(review['user']['login'])



data = {
    "Commit Message": commit_messages_list,
    "Employee Name": employee_name,
    "Employee Email": employee_email,
    "Date": commit_date,
    "Reviewer Name" : approved_users
}

df = pd.DataFrame(data)
df.to_csv("output.csv", index=False)

print("Done.")
