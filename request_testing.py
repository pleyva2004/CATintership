import requests
from requests.auth import HTTPBasicAuth

# Setup
organization = 'cat-digital-applications'
project = 'CRM' 
pat = 'wjwvvkcbz72nnkam5uao6udcmabo6btzitdznitrgn3qj6xczjiq'

# Azure DevOps REST API endpoint for retrieving teams in a project
url = f'https://dev.azure.com/{organization}/_apis/projects/{project}/teams?api-version=6.0'

# Making the GET request
response = requests.get(url, auth=HTTPBasicAuth('', pat))

#Function to get all teams
def get_teams():
      # Check if the request was successful
      if response.status_code == 200:
            teams = response.json()
            for team in teams['value']:
                  #print(f"Team name: {team['name']}, ID: {team['id']}")
                  get_members(team['name'])
      else:
            print(f"Failed to retrieve teams. Status code: {response.status_code}")
            #print(response.text)

# Function to get story points for work items assigned to a member
def get_story_points(member_id, organization, project, pat):
    # Azure DevOps REST API endpoint for querying work items
    url = f'https://dev.azure.com/{organization}/{project}/_apis/wit/wiql?api-version=6.0'
    
    # WIQL query to find work items assigned to the member
    query = {
        "query": f"SELECT [System.Id], [Microsoft.VSTS.Scheduling.StoryPoints] FROM WorkItems WHERE [System.AssignedTo] = '{member_id}'"
    }
    
    # Making the POST request
    response = requests.post(url, json=query, auth=HTTPBasicAuth('', pat))
    
    # Check if the request was successful
    if response.status_code == 200:
        work_items = response.json()
        story_points = {}
        
        for item in work_items.get('workItems', []):
            item_id = item['id']
            # Get detailed information about each work item
            item_url = f'https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/{item_id}?api-version=6.0'
            item_response = requests.get(item_url, auth=HTTPBasicAuth('', pat))
            
            if item_response.status_code == 200:
                item_details = item_response.json()
                story_point = item_details.get('fields', {}).get('Microsoft.VSTS.Scheduling.StoryPoints', 0)
                story_points[item_id] = story_point
            else:
                print(f"Failed to retrieve work item {item_id}. Status code: {item_response.status_code}")
                print(item_response.text)
                
        return story_points
    else:
        print(f"Failed to query work items. Status code: {response.status_code}")
        print(response.text)
        return {}

# Funciton to get all members 
def get_members(team_name):
      url = f'https://dev.azure.com/{organization}/_apis/projects/{project}/teams/{team_name}/members?api-version=6.0'

      # Check if the request was successful
      if response.status_code == 200:
            team_members = response.json()
     
            #for member in team_members['value']:
                  #print(f"ID: {member['id']}")

            for member in team_members.get('value', []):
                  member_id = member.get('id', 'N/A')
                  display_name = member.get('displayName', 'N/A')
                  unique_name = member.get('uniqueName', 'N/A')
                  #print(f"Team Name: {team_name}  |  ID: {member_id}")

                  story_points = get_story_points(member_id, organization, project, pat)
                  print(f"Member ID: {member_id}, Story Points: {story_points}")
      else:
            print(f"Failed to retrieve teams. Status code: {response.status_code}")

      # Execute


get_teams()

