"""
GitHub Read Access Granter
This script grants read access to existing repositories in a GitHub organization.

Requirements:
- pip install pandas openpyxl PyGithub

Usage:
1. Prepare repo_readaccess.xlsx with columns: Repository, GITHUB ID
2. Set your GitHub Personal Access Token as an environment variable: GITHUB_TOKEN
3. Run: python grant_read_access.py
"""

import os
import pandas as pd
from github import Github, GithubException
import time

# Configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
ORG_NAME = 'SENG312-2026'
EXCEL_FILE = 'repo_readaccess.xlsx'

def read_access_list_from_excel(file_path):
    """
    Read repository access information from Excel file.
    Expected columns: Repository, GITHUB ID
    Returns: dict with repo names as keys and list of GitHub IDs as values
    """
    try:
        df = pd.read_excel(file_path)
        print(f"Excel columns found: {df.columns.tolist()}")
        
        # Organize data by repository
        repo_access = {}
        current_repo = None
        
        for index, row in df.iterrows():
            # Check for repository name (try different possible column names)
            repo = row.get('Repository') or row.get('repository') or row.get('Repo') or row.get('repo') or row.get('Repo Name') or row.get('repo name')
            github_id = row.get('GITHUB ID') or row.get('GitHub ID') or row.get('github_id') or row.get('github id') or row.get('GithubID') or row.get('githubid')
            
            # Update current repository if this row contains repo info
            if not pd.isna(repo):
                repo_str = str(repo).strip()
                if repo_str and repo_str.lower() != 'nan':
                    current_repo = repo_str
                    if current_repo not in repo_access:
                        repo_access[current_repo] = []
            
            # Add GitHub ID to current repository if valid
            if current_repo and not pd.isna(github_id):
                github_id_str = str(github_id).strip()
                # Skip empty or invalid entries
                if github_id_str and github_id_str.lower() != 'nan':
                    # Clean GitHub ID (remove whitespace, @, etc.)
                    github_id_clean = github_id_str.replace('@', '').replace(' ', '')
                    if github_id_clean not in repo_access[current_repo]:
                        repo_access[current_repo].append(github_id_clean)
        
        return repo_access
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found!")
        print("Please make sure the Excel file exists in the current directory.")
        raise
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        raise

def grant_read_access(repo, github_username):
    """
    Grant read (pull) access to a user for the repository.
    """
    try:
        # Check if user already has access
        try:
            permission = repo.get_collaborator_permission(github_username)
            if permission in ['admin', 'write', 'read']:
                print(f"  ℹ {github_username} already has {permission} access, skipping...")
                return True
        except GithubException:
            pass  # User doesn't have access, proceed to add them
        
        # Add collaborator with read (pull) permission
        repo.add_to_collaborators(github_username, permission='pull')
        print(f"  ✓ Granted read access to {github_username}")
        time.sleep(0.5)  # Rate limiting
        return True
    except GithubException as e:
        if e.status == 404:
            print(f"  ✗ User {github_username} not found on GitHub")
        else:
            print(f"  ✗ Error granting access to {github_username}: {e}")
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
    
    # Read access list from Excel
    print(f"Reading access list from {EXCEL_FILE}...")
    try:
        repo_access = read_access_list_from_excel(EXCEL_FILE)
    except Exception:
        return
    
    print(f"\nFound {len(repo_access)} repositories:")
    for repo_name, users in repo_access.items():
        print(f"  {repo_name}: {len(users)} user(s) - {', '.join(users)}")
    print()
    
    # Grant read access to repositories
    print("=" * 60)
    print("Granting read access to repositories...")
    print("=" * 60)
    
    total_repos = len(repo_access)
    successful_repos = 0
    failed_repos = []
    
    for repo_name, users in repo_access.items():
        print(f"\n📁 Processing repository: {repo_name}")
        
        # Get repository
        try:
            repo = org.get_repo(repo_name)
            print(f"  ✓ Repository found")
        except GithubException as e:
            if e.status == 404:
                print(f"  ✗ Repository '{repo_name}' not found in organization!")
                failed_repos.append(repo_name)
                continue
            else:
                print(f"  ✗ Error accessing repository: {e}")
                failed_repos.append(repo_name)
                continue
        
        # Grant access to each user
        success_count = 0
        for github_id in users:
            if grant_read_access(repo, github_id):
                success_count += 1
        
        if success_count == len(users):
            successful_repos += 1
            print(f"  ✓ Successfully granted access to all {len(users)} user(s)")
        else:
            print(f"  ⚠ Granted access to {success_count}/{len(users)} user(s)")
        
        time.sleep(1)  # Rate limiting between repositories
    
    # Summary
    print("\n" + "=" * 60)
    print("✓ Read access granting complete!")
    print("=" * 60)
    print(f"\nSummary:")
    print(f"  Total repositories: {total_repos}")
    print(f"  Successful: {successful_repos}")
    print(f"  Failed: {len(failed_repos)}")
    
    if failed_repos:
        print(f"\nFailed repositories:")
        for repo_name in failed_repos:
            print(f"  - {repo_name}")
    
    print(f"\nOrganization repositories: https://github.com/orgs/{ORG_NAME}/repositories")

if __name__ == "__main__":
    main()
