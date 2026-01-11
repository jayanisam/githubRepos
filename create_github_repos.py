"""
GitHub Repository Creator for Team Projects
This script creates private repositories in a GitHub organization and adds team members with write access.

Requirements:
- pip install pandas openpyxl PyGithub

Usage:
1. Set your GitHub Personal Access Token as an environment variable: GITHUB_TOKEN
2. Run: python create_github_repos.py
"""

import os
import pandas as pd
from github import Github, GithubException
import time

# Configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
ORG_NAME = 'SENG321-2026'
EXCEL_FILE = 'Teams List.xlsx'
NUM_TEAMS = 8

def read_teams_from_excel(file_path):
    """
    Read team information from Excel file.
    Expected columns: Team, GITHUB ID (and other columns)
    """
    try:
        df = pd.read_excel(file_path)
        print(f"Excel columns found: {df.columns.tolist()}")
        
        # Organize data by team
        teams = {}
        current_team = None
        
        for index, row in df.iterrows():
            # Check all possible column names for team info
            team = row.get('Team') or row.get('team') or row.get('Unnamed: 0')
            github_id = row.get('GITHUB ID') or row.get('GitHub ID') or row.get('github_id')
            
            # Update current team if this row contains team info
            if not pd.isna(team):
                team_str = str(team).strip()
                if 'team' in team_str.lower():
                    # Extract team number (e.g., "Team 1" -> 1, "Team 1- B215" -> 1)
                    import re
                    match = re.search(r'team\s*(\d+)', team_str, re.IGNORECASE)
                    if match:
                        current_team = int(match.group(1))
            
            # Add GitHub ID to current team if valid
            if current_team and not pd.isna(github_id):
                github_id_str = str(github_id).strip()
                # Skip empty or invalid entries
                if github_id_str and github_id_str.lower() != 'nan':
                    if current_team not in teams:
                        teams[current_team] = []
                    # Clean GitHub ID (remove whitespace, @, etc.)
                    github_id_clean = github_id_str.replace('@', '').replace(' ', '')
                    teams[current_team].append(github_id_clean)
        
        return teams
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        raise

def create_repository(g, org, repo_name, description):
    """
    Create a private repository in the organization.
    """
    try:
        repo = org.create_repo(
            name=repo_name,
            description=description,
            private=True,
            auto_init=True  # Initialize with README
        )
        print(f"✓ Created repository: {repo_name}")
        return repo
    except GithubException as e:
        if e.status == 422:
            print(f"⚠ Repository {repo_name} already exists, fetching it...")
            repo = org.get_repo(repo_name)
            return repo
        else:
            print(f"✗ Error creating {repo_name}: {e}")
            return None

def add_collaborator(repo, github_username, permission='push'):
    """
    Add a collaborator to the repository with specified permission.
    permission: 'pull', 'push', 'admin', 'maintain', 'triage'
    """
    try:
        repo.add_to_collaborators(github_username, permission=permission)
        print(f"  ✓ Added {github_username} with {permission} access")
        time.sleep(0.5)  # Rate limiting
        return True
    except GithubException as e:
        print(f"  ✗ Error adding {github_username}: {e}")
        return False

def main():
    # Validate GitHub token
    if not GITHUB_TOKEN:
        print("ERROR: GITHUB_TOKEN environment variable not set!")
        print("\nTo set your token:")
        print("  Windows (PowerShell): $env:GITHUB_TOKEN='your_token_here'")
        print("  Linux/Mac: export GITHUB_TOKEN='your_token_here'")
        print("\nCreate a token at: https://github.com/settings/tokens")
        print("Required scopes: repo, admin:org")
        return
    
    # Initialize GitHub API
    try:
        g = Github(GITHUB_TOKEN)
        user = g.get_user()
        print(f"Authenticated as: {user.login}")
    except GithubException as e:
        print(f"Authentication failed: {e}")
        return
    
    # Get organization
    try:
        org = g.get_organization(ORG_NAME)
        print(f"Organization: {org.login}\n")
    except GithubException as e:
        print(f"Error accessing organization {ORG_NAME}: {e}")
        return
    
    # Read teams from Excel
    print(f"Reading teams from {EXCEL_FILE}...")
    teams = read_teams_from_excel(EXCEL_FILE)
    print(f"\nFound {len(teams)} teams:")
    for team_num, members in sorted(teams.items()):
        print(f"  Team {team_num}: {len(members)} members - {', '.join(members)}")
    print()
    
    # Create repositories and add team members
    print("=" * 60)
    print("Creating repositories and adding team members...")
    print("=" * 60)
    
    for team_num in range(1, NUM_TEAMS + 1):
        if team_num not in teams:
            print(f"\n⚠ Warning: Team {team_num} not found in Excel file, skipping...")
            continue
        
        team_members = teams[team_num]
        print(f"\n📁 Processing Team {team_num} ({len(team_members)} members)")
        
        # Create Client repository
        client_repo_name = f"Client{team_num}"
        client_repo = create_repository(
            g, org, client_repo_name,
            f"Client repository for Team {team_num}"
        )
        
        if client_repo:
            for member in team_members:
                add_collaborator(client_repo, member, permission='push')
        
        # Create Designer repository
        designer_repo_name = f"Designer{team_num}"
        designer_repo = create_repository(
            g, org, designer_repo_name,
            f"Designer repository for Team {team_num}"
        )
        
        if designer_repo:
            for member in team_members:
                add_collaborator(designer_repo, member, permission='push')
        
        time.sleep(1)  # Rate limiting between teams
    
    print("\n" + "=" * 60)
    print("✓ Repository setup complete!")
    print("=" * 60)
    print(f"\nCreated repositories can be viewed at:")
    print(f"https://github.com/orgs/{ORG_NAME}/repositories")

if __name__ == "__main__":
    main()
