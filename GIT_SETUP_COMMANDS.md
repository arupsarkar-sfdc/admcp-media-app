# Git Setup Commands - Nike-Yahoo AdCP Platform

## 📋 What Gets Committed vs Ignored

### ✅ Will Be Committed (Tracked)
- All Python source code (`.py` files)
- Documentation (`.md` files)
- Database schema (`schema.sql`)
- Database with sample data (`adcp_platform.db`) - 144 KB
- Configuration templates (`env.template`)
- Project configuration (`pyproject.toml`)

### ❌ Will Be Ignored (Not Committed)
- **Environment files** (`.env`) - Contains API keys! 🔒
- Python cache (`__pycache__/`, `*.pyc`)
- IDE files (`.vscode/`, `.idea/`)
- OS files (`.DS_Store`, `Thumbs.db`)
- Virtual environments (`venv/`, `.venv/`)
- Log files (`*.log`)

---

## 🚀 Git Initialization Commands

### Step 1: Navigate to Project Directory

```bash
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app
```

### Step 2: Verify .gitignore Exists

```bash
ls -la .gitignore
```

Should show: `.gitignore` file created

### Step 3: Initialize Git Repository

```bash
git init
```

**Output:**
```
Initialized empty Git repository in /Users/arup.sarkar/Projects/Salesforce/admcp-media-app/.git/
```

**What this does:** Creates a hidden `.git/` folder to track changes.

### Step 4: Check Current Status

```bash
git status
```

**Output:** Shows all untracked files (red text)

### Step 5: Configure Git User (First Time Only)

If you haven't configured git globally:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@salesforce.com"
```

Or configure just for this repository:

```bash
git config user.name "Arup Sarkar"
git config user.email "arup.sarkar@salesforce.com"
```

### Step 6: Check What Will Be Committed

```bash
git status
```

Verify that:
- ✅ Python files are listed
- ✅ Markdown files are listed
- ❌ `.env` files are NOT listed (if they exist)
- ❌ `__pycache__/` is NOT listed

### Step 7: Stage All Files

```bash
git add .
```

**What this does:** Stages all untracked files (except those in `.gitignore`)

**Alternative:** Add files selectively:
```bash
git add database/
git add yahoo_mcp_server/
git add *.md
git add .gitignore
```

### Step 8: Verify Staged Files

```bash
git status
```

**Output:** Shows files in green (staged for commit)

### Step 9: Make First Commit

```bash
git commit -m "Initial commit: Nike-Yahoo AdCP Platform

- Phase 1: Database with SQLite and sample data (850K matched users)
- Phase 2: Yahoo MCP Server with FastMCP and LLM integration
- Clean Room workflow simulation with matched audiences
- AdCP Media Buy Protocol implementation
- Documentation and setup guides"
```

**Output:**
```
[master (root-commit) abc1234] Initial commit: Nike-Yahoo AdCP Platform
 XX files changed, XXXX insertions(+)
 create mode 100644 .gitignore
 create mode 100644 BUILD_PHASE_1_DATABASE.md
 ...
```

### Step 10: Verify Commit

```bash
git log
```

Shows your commit with message, date, author.

Or use pretty format:
```bash
git log --oneline
```

---

## 🌿 Optional: Rename Branch to 'main'

Git initializes with `master` by default. To rename to `main`:

```bash
git branch -M main
```

---

## 📦 Optional: Connect to GitHub/Remote

If you want to push to GitHub or another remote repository:

### Step 1: Create Repository on GitHub

Go to GitHub and create a new repository (don't initialize with README).

### Step 2: Add Remote

```bash
git remote add origin https://github.com/YOUR_USERNAME/admcp-media-app.git
```

Or with SSH:
```bash
git remote add origin git@github.com:YOUR_USERNAME/admcp-media-app.git
```

### Step 3: Verify Remote

```bash
git remote -v
```

**Output:**
```
origin  https://github.com/YOUR_USERNAME/admcp-media-app.git (fetch)
origin  https://github.com/YOUR_USERNAME/admcp-media-app.git (push)
```

### Step 4: Push to Remote

```bash
git push -u origin main
```

**What this does:** 
- Uploads your code to GitHub
- Sets `main` as the default upstream branch

---

## 🔍 Useful Git Commands

### Check Status
```bash
git status
```
Shows modified, staged, and untracked files.

### View Commit History
```bash
git log
git log --oneline --graph --all
```

### View What Changed
```bash
git diff                    # Unstaged changes
git diff --staged           # Staged changes
git diff HEAD               # All changes
```

### Stage Specific Files
```bash
git add filename.py
git add folder/
```

### Unstage Files
```bash
git restore --staged filename.py
git reset HEAD filename.py
```

### Discard Changes
```bash
git restore filename.py     # Discard unstaged changes
git checkout -- filename.py # Alternative syntax
```

### Create New Branch
```bash
git branch feature-name
git checkout feature-name

# Or create and switch in one command
git checkout -b feature-name
```

### Switch Branches
```bash
git checkout main
git checkout feature-name
```

### View Branches
```bash
git branch                  # Local branches
git branch -a               # All branches (including remote)
```

### Delete Branch
```bash
git branch -d feature-name  # Safe delete (merged only)
git branch -D feature-name  # Force delete
```

---

## 🔒 Security Checklist

Before committing, verify:

- [ ] `.env` files are NOT staged (`git status` should not show `.env`)
- [ ] API keys are NOT in any committed files
- [ ] `.gitignore` includes `.env`
- [ ] Test tokens are for development only (`nike_token_12345`)
- [ ] No sensitive credentials in code

**Check for sensitive data:**
```bash
git grep -i "api.key"
git grep -i "secret"
git grep -i "password"
```

---

## 📊 What's Being Tracked

### Database Files
```bash
git ls-files database/
```

**Output:**
```
database/adcp_platform.db     # 144 KB - Sample data
database/schema.sql
database/seed_data.py
database/verify_data.py
```

### MCP Server Files
```bash
git ls-files yahoo_mcp_server/
```

**Output:** All `.py` files, `pyproject.toml`, `env.template`, etc.

### Documentation Files
```bash
git ls-files *.md
```

**Output:** All markdown documentation files.

---

## 🔄 Making Changes Later

When you make changes to files:

```bash
# 1. Check what changed
git status
git diff

# 2. Stage changes
git add .
# Or stage specific files
git add file1.py file2.py

# 3. Commit with message
git commit -m "Add feature X"

# 4. Push to remote (if configured)
git push
```

---

## 📝 Commit Message Best Practices

Good commit messages:
```bash
git commit -m "Add LLM fallback to OpenAI when Gemini fails"
git commit -m "Fix: Handle empty product list in discovery service"
git commit -m "Update documentation with SQL verification examples"
```

Bad commit messages:
```bash
git commit -m "fix"
git commit -m "updates"
git commit -m "asdf"
```

**Format:**
```
<type>: <short description>

<optional longer description>
```

**Types:** feat, fix, docs, refactor, test, chore

---

## 🆘 Common Issues

### Issue: "fatal: not a git repository"
**Cause:** Not in project directory or git not initialized
**Fix:**
```bash
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app
git init
```

### Issue: ".env file is being tracked"
**Cause:** File was added before .gitignore
**Fix:**
```bash
git rm --cached .env
git rm --cached yahoo_mcp_server/.env
git commit -m "Remove .env files from tracking"
```

### Issue: "Too many files changed"
**Cause:** `__pycache__` or `venv/` being tracked
**Fix:**
```bash
git rm -r --cached __pycache__/
git rm -r --cached venv/
git commit -m "Remove cache and venv from tracking"
```

### Issue: Want to undo last commit
**Fix (keep changes):**
```bash
git reset --soft HEAD~1
```

**Fix (discard changes):**
```bash
git reset --hard HEAD~1  # ⚠️ DANGEROUS - Cannot undo!
```

---

## 📚 Git Configuration Files Created

After running these commands, you'll have:

```
admcp-media-app/
├── .git/                 # Git repository (hidden folder)
├── .gitignore           # Files to ignore
└── [all your files]     # Tracked by git
```

---

## ✅ Verification Commands

After setup, run these to verify:

```bash
# 1. Check git is initialized
ls -la .git/

# 2. Check gitignore works
git status | grep -i ".env"     # Should return nothing

# 3. Check commit history
git log --oneline

# 4. Check tracked files
git ls-files | wc -l            # Count tracked files

# 5. Check repository size
du -sh .git/
```

---

## 🎯 Summary of All Commands

```bash
# Navigate to project
cd /Users/arup.sarkar/Projects/Salesforce/admcp-media-app

# Initialize git
git init

# Configure user (if needed)
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Stage all files
git add .

# Check what will be committed
git status

# Make first commit
git commit -m "Initial commit: Nike-Yahoo AdCP Platform"

# Rename branch to main (optional)
git branch -M main

# View history
git log --oneline

# Optional: Add remote and push
# git remote add origin YOUR_REPO_URL
# git push -u origin main
```

---

## 🎓 Next Steps

After git setup:
1. ✅ Git repository initialized
2. ✅ First commit made
3. ➡️ Continue with Phase 2: Yahoo MCP Server
4. ⏳ Future commits as you develop

**Remember:** Always check `git status` before committing to ensure no sensitive files!

---

**Last Updated:** November 17, 2025
**Git Version Required:** 2.0+

