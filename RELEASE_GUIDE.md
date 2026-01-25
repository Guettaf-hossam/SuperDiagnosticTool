# 🚀 Quick Release Guide for v1.0.1

## Option 1: Automatic (Recommended)

### Windows PowerShell:
```powershell
.\release_v1.0.1.ps1
```

### Git Bash:
```bash
bash release_v1.0.1.sh
```

---

## Option 2: Manual Steps

### 1️⃣ Commit Changes
```bash
git add .
git commit -m "v1.0.1 - Critical Hotfix: API Key Persistence"
```

### 2️⃣ Create Tag
```bash
git tag -a v1.0.1 -m "v1.0.1 - Critical Hotfix"
```

### 3️⃣ Push to GitHub
```bash
git push origin main
git push origin v1.0.1
```

### 4️⃣ Build Executable (Optional)
```bash
python build.py
```

### 5️⃣ Create GitHub Release
1. Go to: https://github.com/Guettaf-hossam/SuperDiagnosticTool/releases/new?tag=v1.0.1
2. **Title:** `v1.0.1 - Critical Hotfix 🔧`
3. **Description:** Copy from `RELEASE_v1.0.1.md`
4. **Upload:** `dist/SuperDiagnosticTool.exe`
5. Click **"Publish release"**

---

## 📋 Checklist

- [ ] All changes committed
- [ ] Tag v1.0.1 created
- [ ] Pushed to GitHub
- [ ] Executable built (if needed)
- [ ] GitHub release created
- [ ] Release notes added
- [ ] Executable uploaded

---

## 🎯 What This Release Fixes

**Critical Bug:** API key was not persisting between sessions

**Impact:** Users had to re-enter their API key every time they launched the program

**Solution:** 
- Removed destructive regex sanitization
- Added UTF-8 encoding
- Improved error messages

---

## 📞 Need Help?

If you encounter any issues:
1. Check `CHANGELOG.md` for detailed changes
2. Review `RELEASE_v1.0.1.md` for full release notes
3. Open an issue on GitHub
