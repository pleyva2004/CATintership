import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
import pandas as pd
import json


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


# Function to get story points for work items assigned to a member
def get_story_points(assigned_to):
    # Azure DevOps REST API endpoint for querying work items
    url = f'https://dev.azure.com/{organization}/{project}/_apis/wit/wiql?api-version=6.0'

    # Calculate the date one month ago
    creation_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    # WIQL query to find work items assigned to the member
    query = {
        "query": f"SELECT [System.Id], [Microsoft.VSTS.Scheduling.StoryPoints] FROM WorkItems WHERE [System.AssignedTo] = '{assigned_to}'"
    }

    query2 = {
        "query": f"SELECT [System.Id], [System.Title], [System.State] From WorkItems Where [System.AssignedTo] = '{assigned_to}'"
    }

    query3 = {
         "query": f"SELECT [System.Id], [System.Title], [System.State] FROM WorkItems WHERE [System.TeamProject] = '{project}' AND [System.CreatedDate] >= '{creation_date}'"
    }

    # Making the POST request
    response = requests.post(url, json=query2, auth=auth)

    # Check if the request was successful
    if response.status_code == 200:
        query_result = response.json()
        # Get the work item IDs
        work_item_ids = [item['id'] for item in query_result['workItems']]




        for ids in work_item_ids:

            work_items_url = f'https://dev.azure.com/{organization}/_apis/wit/workitems?ids={ids}&api-version=6.0'
            work_items_response = requests.get(work_items_url, auth=HTTPBasicAuth('', pat))

            if work_items_response.status_code == 200:
                work_items_details = work_items_response.json()

                if 'relations' in work_items_details:
                    print("Found")
                break
                # Print work items details for debugging purposes

                # Print work items details
                for item in work_items_details['value']:
                    #print(f"Work Items Details: {json.dumps(work_items_details, indent=2)}")
                    print(f"Work Item ID: {item['id']}")
                    print(item.keys())
                    #print(f"Title: {item['fields']['System.Title']}")
                    #print(f"State: {item['fields']['System.State']}")
                    #print(f"Type: {item['fields']['System.WorkItemType']}")

                    has_external_link = False
                    external_link = None
                    if 'relations' in item:
                        for relation in item['relations']:
                            if relation['rel'] == 'ArtifactLink':
                                has_external_link = True
                                external_link = relation['url']
                                break

                    if has_external_link:
                        print("External Link: Yes")
                        print(f"Link: {external_link}")
                    else:
                        print("External Link: No")
            else:
                print(f"Failed to get work items details: {work_items_response.status_code}")
                print(work_items_response.text)
        else:
            print("No work items found.")


        # Fetch the work items using their IDs
        #work_items_url = f'https://dev.azure.com/{organization}/_apis/wit/workitems?ids={",".join(map(str, work_item_ids))}&api-version=6.0'

        #work_items_response = requests.get(work_items_url, auth=auth)

        #if work_items_response.status_code == 200:
            #work_items = work_items_response.json()
            #print(json.dumps(work_items, indent=4))
        #else:
            #print(f'Error fetching work items: {work_items_response.status_code}')
        # print(work_items_response.json())

        # for item in work_items.get('workItems', []):
        #   item_id = item['id']
        # Get detailed information about each work item
        #  item_url = f'https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/{item_id}?api-version=6.0'
        # item_response = requests.get(item_url, auth=HTTPBasicAuth('', pat))

        # if item_response.status_code == 200:
        #   item_details = item_response.json()
        #  story_point = item_details.get('fields', {}).get('Microsoft.VSTS.Scheduling.StoryPoints', 0)
        # story_points[item_id] = story_point
        # else:
        #   print(f"Failed to retrieve work item {item_id}. Status code: {item_response.status_code}")
        #  print(item_response.text)

        # return story_points
    else:
        print(f"Failed to query work items. Status code: {response.status_code}")
        # print(response.text)
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

get_story_points('arpitha.jh@cat.com')
