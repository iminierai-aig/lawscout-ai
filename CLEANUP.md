# Pre-GitHub Cleanup Checklist

## Files to Delete Before Committing

Run these commands to clean up before creating your GitHub repo:

```bash
# Remove backup files
find . -type f \( -name "*.bak" -o -name "*.OLD" -o -name "*.backup" \) -not -path "./.venv/*" -delete

# Remove log files
rm -f *.log collection_100k.log

# Remove backup directory
rm -rf lawscout-ai.backup/

# Remove Python cache
find . -type d -name "__pycache__" -not -path "./.venv/*" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -not -path "./.venv/*" -delete

# Remove test/utility scripts if not needed
# rm -f verify_embeddings.py  # Uncomment if you don't want this in the repo
```

## Already Excluded (via .gitignore)

✅ Large data directories (data/, qdrant_storage/)
✅ Virtual environment (.venv/)
✅ Credentials (.env, *.key)
✅ Log files (*.log)
✅ Backup files (*.bak, *.OLD)
✅ Python cache (__pycache__/)

## Optional: Create .gitkeep files

If you want empty directories to be tracked:

```bash
touch data/.gitkeep
touch qdrant_storage/.gitkeep
touch reports/.gitkeep
```

## Verify Before Pushing

```bash
# Check what will be committed
git status

# Check for any large files
find . -type f -size +10M -not -path "./.venv/*" -not -path "./.git/*"

# Check for sensitive data
grep -r "api_key\|API_KEY\|password\|PASSWORD\|secret\|SECRET" --include="*.py" --include="*.md" --exclude-dir=".venv" .
```
