# Quick Release Checklist for v1.0.1

## Pre-Release

- [x] All bugs fixed and tested
- [x] API key persistence verified
- [x] Environment variable issue resolved
- [x] Project cleaned (test files removed)
- [x] CHANGELOG.md updated
- [x] RELEASE_v1.0.1.md created
- [ ] Build executable with `python build.py`
- [ ] Test executable on clean system

## Git Commands

```bash
# 1. Stage all changes
git add .

# 2. Commit
git commit -m "v1.0.1 - Critical Hotfix: API Key Persistence

Fixed three critical issues:
- Over-aggressive regex sanitization corrupting keys
- Working directory confusion causing inconsistent save locations  
- Environment variable conflict with old keys

All API key operations now use UTF-8 encoding and script directory.
Improved error handling and user feedback."

# 3. Create tag
git tag -a v1.0.1 -m "v1.0.1 - Critical Hotfix

Fixes:
- API key persistence across sessions
- Key corruption from regex sanitization
- Directory confusion from os.getcwd()
- Environment variable conflicts

Improvements:
- UTF-8 encoding for all file operations
- Visible input with Ctrl+V support
- Better error messages and validation
- Auto-cleanup of corrupted keys"

# 4. Push to GitHub
git push origin main
git push origin v1.0.1
```

## GitHub Release

1. **Go to:** https://github.com/Guettaf-hossam/SuperDiagnosticTool/releases/new?tag=v1.0.1

2. **Title:** `v1.0.1 - Critical Hotfix 🔧`

3. **Description:** Copy from `RELEASE_v1.0.1.md`

4. **Upload:**
   - `dist/SuperDiagnosticTool.exe`

5. **Publish Release**

## Post-Release

- [ ] Test download link
- [ ] Update README.md badges if needed
- [ ] Notify users of important fix
- [ ] Close related issues on GitHub

---

## Quick Command

```powershell
# Build and prepare for release
python build.py
git add .
git commit -m "v1.0.1 - Critical Hotfix: API Key Persistence"
git tag -a v1.0.1 -m "v1.0.1 - Critical Hotfix"
git push origin main  
git push origin v1.0.1
```
