# GitHub Repository Setup for Teams

This script automates the creation of private repositories in the `TJay-est-org` GitHub organization and adds team members with write access.

## What it does

- Creates 16 private repositories: `Client1-8` and `Designer1-8`
- Reads team member GitHub IDs from `Teams List.xlsx`
- Adds each team member to their team's two repositories with write access
- Handles existing repositories gracefully

## Prerequisites

### 1. GitHub Personal Access Token

You need a GitHub Personal Access Token with the following permissions:
- `repo` (Full control of private repositories)
- `admin:org` (Full control of orgs and teams)

**Create a token:**
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Set an expiration date
4. Select scopes: `repo` and `admin:org`
5. Click "Generate token"
6. Copy the token immediately (you won't see it again!)

### 2. Organization Access

You must have owner or admin access to the `TJay-est-org` organization.

## Installation

1. Install Python dependencies:
```powershell
pip install -r requirements.txt
```

## Usage

### Step 1: Set your GitHub token

**PowerShell (Windows):**
```powershell
$env:GITHUB_TOKEN='your_personal_access_token_here'
```

**Command Prompt (Windows):**
```cmd
set GITHUB_TOKEN=your_personal_access_token_here
```

**Linux/Mac:**
```bash
export GITHUB_TOKEN='your_personal_access_token_here'
```

### Step 2: Run the script

```powershell
python create_github_repos.py
```

## Expected Excel Format

The `Teams List.xlsx` file should have at least these columns:
- `Team` - Team number or name (e.g., "Team 1", "1", etc.)
- `GITHUB ID` - GitHub username (without @)

Example:
| Team | Name | GITHUB ID |
|------|------|-----------|
| 1 | John | john_doe |
| 1 | Jane | jane_smith |
| 2 | Bob | bob_jones |

## What happens when you run it

1. Authenticates with GitHub using your token
2. Reads team information from Excel file
3. For each team (1-8):
   - Creates `Client{X}` repository
   - Creates `Designer{X}` repository
   - Adds all team members with write access to both repos
4. Reports success/errors for each operation

## Troubleshooting

### "GITHUB_TOKEN environment variable not set"
Set your token as shown in Step 1 above.

### "Authentication failed"
- Check your token is valid
- Ensure token has correct permissions (`repo`, `admin:org`)

### "Error accessing organization"
- Verify you have owner/admin access to `TJay-est-org`
- Check organization name is spelled correctly

### "Error adding collaborator"
- GitHub username might not exist
- User might need to accept the invitation
- Check for typos in GitHub IDs in the Excel file

## Notes

- The script includes rate limiting delays to avoid GitHub API limits
- Existing repositories will be reused (not recreated)
- Team members receive invitations and must accept them to access private repos
- `push` permission = write access (can push/pull code)
