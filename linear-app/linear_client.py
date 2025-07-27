import os
import requests
from dotenv import load_dotenv

load_dotenv()

class LinearClient:
    def __init__(self):
        self.api_key = os.getenv('LINEAR_API_KEY')
        if not self.api_key:
            raise ValueError("LINEAR_API_KEY not found in environment variables")
        
        self.base_url = "https://api.linear.app/graphql"
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
    
    def query(self, query_string, variables=None):
        payload = {
            "query": query_string
        }
        if variables:
            payload["variables"] = variables
        
        response = requests.post(self.base_url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_viewer(self):
        query = """
        query {
            viewer {
                id
                name
                email
            }
        }
        """
        return self.query(query)
    
    def get_teams(self):
        query = """
        query {
            teams {
                nodes {
                    id
                    name
                    key
                }
            }
        }
        """
        return self.query(query)
    
    def get_issues(self, first=10):
        query = """
        query($first: Int!) {
            issues(first: $first) {
                nodes {
                    id
                    title
                    description
                    state {
                        name
                    }
                    assignee {
                        name
                    }
                    createdAt
                    updatedAt
                }
            }
        }
        """
        return self.query(query, {"first": first})
    
    def create_issue(self, team_id, title, description=None):
        mutation = """
        mutation($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                success
                issue {
                    id
                    title
                    description
                }
            }
        }
        """
        variables = {
            "input": {
                "teamId": team_id,
                "title": title
            }
        }
        if description:
            variables["input"]["description"] = description
        
        return self.query(mutation, variables)


if __name__ == "__main__":
    client = LinearClient()
    
    print("Testing Linear API connection...")
    print("\n1. Getting viewer info:")
    viewer = client.get_viewer()
    print(f"   Connected as: {viewer['data']['viewer']['name']} ({viewer['data']['viewer']['email']})")
    
    print("\n2. Getting teams:")
    teams = client.get_teams()
    for team in teams['data']['teams']['nodes']:
        print(f"   - {team['name']} (key: {team['key']})")
    
    print("\n3. Getting recent issues:")
    issues = client.get_issues(5)
    for issue in issues['data']['issues']['nodes']:
        assignee_name = issue['assignee']['name'] if issue['assignee'] else "Unassigned"
        print(f"   - {issue['title']} (State: {issue['state']['name']}, Assignee: {assignee_name})")