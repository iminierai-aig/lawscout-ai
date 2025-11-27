# 🚀 GitHub Repository Setup Guide

## Prerequisites

1. **GitHub CLI** (recommended) - Install: `brew install gh` (Mac) or see https://cli.github.com
2. **OR** GitHub account with personal access token

---

## Method 1: Using GitHub CLI (Easiest) ⭐

### Step 1: Authenticate GitHub CLI
```bash
gh auth login
# Follow the prompts to authenticate
```

### Step 2: Clean up the project
```bash
./cleanup_for_github.sh
```

### Step 3: Initialize Git (if not already done)
```bash
cd /Users/admin/lawscout-ai
git init
```

### Step 4: Add all files
```bash
git add .
```

### Step 5: Create initial commit
```bash
git commit -m "Initial commit: LawScout AI - Legal Research RAG System"
```

### Step 6: Create private repo and push
```bash
# Create private repo and push in one command
gh repo create lawscout-ai --private --source=. --remote=origin --push

# OR if you want to specify description
gh repo create lawscout-ai \
  --private \
  --description "AI-Powered Legal Research for Solo Practitioners & Small Law Firms" \
  --source=. \
  --remote=origin \
  --push
```

**Done!** Your repo is now on GitHub.

---

## Method 2: Using Git + GitHub API (Alternative)

### Step 1: Clean up the project
```bash
./cleanup_for_github.sh
```

### Step 2: Initialize Git
```bash
cd /Users/admin/lawscout-ai
git init
git add .
git commit -m "Initial commit: LawScout AI - Legal Research RAG System"
```

### Step 3: Create private repo via API
```bash
# Set your GitHub username and token
export GITHUB_USERNAME="your-username"
export GITHUB_TOKEN="your-personal-access-token"

# Create private repository
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d '{
    "name": "lawscout-ai",
    "description": "AI-Powered Legal Research for Solo Practitioners & Small Law Firms",
    "private": true
  }'
```

### Step 4: Add remote and push
```bash
git remote add origin https://github.com/$GITHUB_USERNAME/lawscout-ai.git
git branch -M main
git push -u origin main
```

---

## Method 3: Manual GitHub Web + Git Push

### Step 1: Clean up
```bash
./cleanup_for_github.sh
```

### Step 2: Initialize Git
```bash
cd /Users/admin/lawscout-ai
git init
git add .
git commit -m "Initial commit: LawScout AI - Legal Research RAG System"
```

### Step 3: Create repo on GitHub.com
1. Go to https://github.com/new
2. Repository name: `lawscout-ai`
3. Description: "AI-Powered Legal Research for Solo Practitioners & Small Law Firms"
4. Select **Private**
5. **DO NOT** initialize with README, .gitignore, or license (you already have these)
6. Click "Create repository"

### Step 4: Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/lawscout-ai.git
git branch -M main
git push -u origin main
```

---

## Quick One-Liner (GitHub CLI Method)

If you've already cleaned up and initialized git:

```bash
gh repo create lawscout-ai --private --source=. --remote=origin --push
```

---

## Verify Everything Worked

```bash
# Check remote
git remote -v

# Check status
git status

# View repo on GitHub
gh repo view --web
```

---

## Troubleshooting

### If you get "repository already exists"
```bash
# Remove existing remote
git remote remove origin

# Create with different name or delete existing repo first
gh repo delete lawscout-ai --yes  # ⚠️ Deletes the repo!
```

### If you need to update .gitignore after pushing
```bash
# Add new patterns to .gitignore
git add .gitignore
git commit -m "Update .gitignore"
git push
```

### If you forgot to clean up first
```bash
# Run cleanup
./cleanup_for_github.sh

# Remove files from git cache (if already committed)
git rm -r --cached lawscout-ai.backup/
git rm --cached *.log
git commit -m "Remove backup files and logs"
git push
```

---

## Next Steps After Pushing

1. **Add repository topics/tags** on GitHub:
   - `legal-tech`
   - `rag`
   - `ai`
   - `legal-research`
   - `python`
   - `streamlit`

2. **Set up GitHub Actions** (optional):
   - Create `.github/workflows/` for CI/CD

3. **Add collaborators** (if needed):
   ```bash
   gh repo edit --add-collaborator USERNAME
   ```

4. **Create releases** (when ready):
   ```bash
   gh release create v0.1.0 --title "Initial Release" --notes "First version of LawScout AI"
   ```

