import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
import pandas as pd

# Setup
organization = 'cat-digital-applications'
project = 'CRM'
pat = 'pat'
auth = HTTPBasicAuth('', pat)


# Function to get all team
def get_teams():
    # Azure DevOps REST API endpoint for retrieving teams in a project
    url = f'https://dev.azure.com/{organization}/_apis/projects/{project}/teams?api-version=6.0'

    # Making the GET request
    response = requests.get(url, auth=auth)

    if response.status_code == 200:
        temp = response.json()
        return temp
    else:
        print(f"Failed to retrieve teams. Status code: {response.status_code}")


# Function to get all members
def get_members(team_name, id_list):
    url = f'https://dev.azure.com/{organization}/_apis/projects/{project}/teams/{team_name}/members?api-version=6.0'

    # Making the GET request
    response = requests.get(url, auth=auth)

    # Check if the request was successful
    if response.status_code == 200:
        team_members = response.json()

        # print(team_members)
        for member in team_members['value']:
            items = list(member.items())
            for i in range(len(items)):
                temp = items[i][1]
                if temp is not True:
                    member_id = temp['id']

                    display_name = temp['displayName']

                    email = temp['uniqueName']

                    if member_id not in id_list:
                        id_list.append(member_id)

                    if display_name not in name_list:
                        name_list.append(display_name)

                    if email not in email_list:
                        email_list.append(email)

                        # dev = (member_id, display_name, email)
                        # employee_list.add(dev)

            # for employee in employee_list:
            # print(f"ID: {employee[0]}, Name: {employee[1]}, Unique Name: {employee[2]} \n")



    else:
        print(f"Failed to retrieve teams. Status code: {response.status_code}")


# Function to convert from iso Date Time -> M/D/Y
def convert_iso_to_date(iso_string: str) -> str:
    date_obj = datetime.fromisoformat(iso_string)

    # Desired format string
    desired_format = "%m-%d-%Y"

    # Convert datetime object to desired format
    formatted_string = date_obj.strftime(desired_format)

    return formatted_string


# Function to get story points for work items assigned to a member
def get_story_points(assigned_to):
    # Azure DevOps REST API endpoint for querying work items
    url = f'https://dev.azure.com/{organization}/{project}/_apis/wit/wiql?api-version=6.0'

    # Calculate the date one month ago
    creation_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    # WIQL query to find work items assigned to the member
    query = {
        "query": f"SELECT [System.Id], [Microsoft.VSTS.Scheduling.StoryPoints] FROM WorkItems WHERE [System.AssignedTo] = '{assigned_to}'"
    }

    query2 = {
        "query": f"SELECT [System.Id], [System.Title], [System.State] From WorkItems Where [System.AssignedTo] = '{assigned_to}'"
    }

    query3 = {
        "query": f"SELECT [System.Id], [System.Title], [System.State] FROM WorkItems WHERE [System.TeamProject] = '{project}' AND [System.CreatedDate] >= @Today - 3 "
    }

    query4 = {
        "query": f"SELECT [System.Id], [System.WorkItemType], [System.Title], [System.AssignedTo], [System.c], [System.Tags], [System.AreaPath],[System.CreatedBy], [System.CreatedDate], [Microsoft.VSTS.Scheduling.StoryPoints], [System.IterationPath], [System.ExternalLinkCount]  FROM WorkItems WHERE [System.TeamProject] = '{project}' AND [System.CreatedDate] >= @Today - 7 "
    }

    query5 = {
        "query": f"SELECT * FROM WorkItems WHERE [System.TeamProject] = '{project}' AND [System.WorkItemType] IN ('Bug', 'User Story') AND [System.State] IN ('12.Ready for UAT', '13.In UAT', '16.Ready to Deploy to Prod','17.Deployed to Prod', 'Closed') AND [System.ExternalLinkCount] == 0 AND [System.CreatedDate] >= @Today - 7 ORDER BY [System.CreatedDate] DESC"
    }

    # Making the POST request
    response = requests.post(url, json=query5, auth=auth)

    # Check if the request was successful
    if response.status_code == 200:
        query_result = response.json()

        global work_item_ids
        # Get the work item IDs
        work_item_ids = [item['id'] for item in query_result['workItems']]


        for ids in work_item_ids:

            # Get the work item details
            work_items_url = f'https://dev.azure.com/{organization}/_apis/wit/workitems?ids={ids}&api-version=6.0'
            work_items_response = requests.get(work_items_url, auth=HTTPBasicAuth('', pat))

            if work_items_response.status_code == 200:
                work_items_details = work_items_response.json()

                # Print work items details

                for item in work_items_details['value']:
                    keys = list(item['fields'].keys())

                    # print(f"Work Item ID: {item['id']}")
                    # work_item_ids.append(item['id'])
                    # print(f"Title: {item['fields']['System.Title']}")
                    work_item_titles.append(item['fields']['System.Title'])
                    # print(f"State: {item['fields']['System.State']}")
                    work_item_states.append(item['fields']['System.State'])
                    # print(f"Type: {item['fields']['System.WorkItemType']}")
                    work_item_types.append(item['fields']['System.WorkItemType'])

                    if 'System.AssignedTo' in keys:
                        name = item['fields']['System.AssignedTo']['displayName']
                        work_item_assignedTo_name.append(name)
                        email = item['fields']['System.AssignedTo']['uniqueName']
                        work_item_assignedTo_email.append(email)
                        worker_id = item['fields']['System.AssignedTo']['id']
                        # print(f"Assigned To: {name}, {email}, {worker_id}")

                    else:
                        work_item_assignedTo_name.append('')
                        work_item_assignedTo_email.append('')

                    if 'System.Tags' in keys:
                        work_item_tags.append(item['fields']['System.Tags'])
                        # print(f"Tags: {item['fields']['System.Tags']}")
                    else:
                        work_item_tags.append('')

                    if 'System.AreaPath' in keys:
                        work_item_area_path.append(item['fields']['System.AreaPath'])
                        # print(f"AreaPath: {item['fields']['System.AreaPath']}")
                    else:
                        work_item_area_path.append('')

                    pm_name = item['fields']['System.CreatedBy']['displayName']
                    work_item_creator_name.append(pm_name)
                    pm_email = item['fields']['System.CreatedBy']['uniqueName']
                    work_item_creator_email.append(pm_email)
                    pm_id = item['fields']['System.CreatedBy']['id']
                    # print(f"Created By: {pm_name}, {pm_email}, {pm_id}")

                    created_date = convert_iso_to_date(item['fields']['System.CreatedDate'])
                    work_item_created_date.append(created_date)
                    # print(f"Created Date: {created_date}")

                    if 'Microsoft.VSTS.Scheduling.StoryPoints' in keys:
                        work_item_story_points.append(item['fields']['Microsoft.VSTS.Scheduling.StoryPoints'])
                        # print(f"StoryPoints: {item['fields']['Microsoft.VSTS.Scheduling.StoryPoints']}")
                    else:
                        work_item_story_points.append('')

                    if 'System.IterationPath' in keys:
                        work_item_iteration_path.append(item['fields']['System.IterationPath'])
                        # print(f"IterationPath: {item['fields']['System.IterationPath']}")
                    else:
                        work_item_iteration_path.append('')

                    # if 'System.ExternalLinkCount' in keys:
                    # print(f"ExternalLinkCount: {item['fields']['System.ExternalLinkCount']}")

            else:
                print(f"Failed to get work items details: {work_items_response.status_code}")
                print(work_items_response.text)
        else:
            print("No work items found.")

    else:
        print(f"Failed to query work items. Status code: {response.status_code}")
        return {}


teams = get_teams()
team_names = []
for team in teams['value']:
    # print(team['name'])
    team_names.append(team['name'])

id_list = []
name_list = []
email_list = []

for team in team_names:
    get_members(team, id_list)

name_email_list = zip(name_list, email_list)

employee_data = dict(zip(id_list, name_email_list))

# print(employee_data[id_list[0]][1])


work_item_ids = []
work_item_titles = []
work_item_states = []
work_item_types = []
work_item_assignedTo_name = []
work_item_assignedTo_email = []
work_item_tags = []
work_item_area_path = []
work_item_creator_name = []
work_item_creator_email = []
work_item_created_date = []
work_item_story_points = []
work_item_iteration_path = []

get_story_points('arpitha.jh@cat.com')

data = {
    "Work Item ID": work_item_ids,
    "Title": work_item_titles,
    "State": work_item_states,
    "Work Item Type": work_item_types,
    "Assigned To Name": work_item_assignedTo_name,
    "Assigned To Email": work_item_assignedTo_email,
    "Tags": work_item_tags,
    "Area Path": work_item_area_path,
    "Creator Name": work_item_creator_name,
    "Creator Email": work_item_creator_email,
    "Created Date": work_item_created_date,
    "Story Points": work_item_story_points,
    "Iteration Path": work_item_iteration_path
}

df = pd.DataFrame(data)
df.to_csv("output_ado.csv", index=False)

print("Done.")
