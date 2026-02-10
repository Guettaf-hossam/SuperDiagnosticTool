# Release Process for SuperDiagnosticTool

This document describes the automated release process for SuperDiagnosticTool.

## Overview

SuperDiagnosticTool uses GitHub Actions to automatically build Windows executables and create releases when you push a version tag.

## How It Works

1. **Push a Version Tag**: When you push a tag like `v1.0.2`, GitHub Actions automatically:
   - Checks out the code
   - Sets up Python on Windows
   - Installs dependencies
   - Builds the Windows executable using PyInstaller
   - Creates a GitHub Release
   - Uploads the .exe file to the release

2. **No Manual Building Required**: You don't need to build the .exe manually on your local machine.

## Release Steps

### 1. Update Documentation

Before creating a release, ensure these files are updated:

- `CHANGELOG.md` - Add the new version entry
- `RELEASE_v{version}.md` - Create release notes
- `RELEASE_CHECKLIST.md` - Update for current version
- `README.md` - Update if there are changes to features or usage

### 2. Commit Your Changes

```bash
git add .
git commit -m "v1.0.2 - Security & Validation Enhancements"
git push origin main
```

### 3. Create and Push a Version Tag

```bash
# Create an annotated tag
git tag -a v1.0.2 -m "v1.0.2 - Security & Validation Enhancements

Enhanced security features:
- Improved API key validation
- HTML sanitization for reports
- Better error handling"

# Push the tag to GitHub
git push origin v1.0.2
```

### 4. Wait for GitHub Actions

- Go to: https://github.com/Guettaf-hossam/SuperDiagnosticTool/actions
- Watch the "Build and Release" workflow run
- It takes about 3-5 minutes to complete

### 5. Verify the Release

- Check: https://github.com/Guettaf-hossam/SuperDiagnosticTool/releases
- The new release should be published with the .exe file attached
- Download and test the executable

## Workflow Details

The GitHub Actions workflow (`.github/workflows/release.yml`) runs on:
- **Trigger**: Push of tags matching `v*.*.*`
- **OS**: Windows (windows-latest)
- **Python**: 3.12
- **Build Tool**: PyInstaller

## Manual Build (For Testing)

If you want to build locally for testing:

### On Windows:
```bash
pip install pyinstaller
pip install -r requirements.txt
python build.py
```

The executable will be in `dist/SuperDiagnosticTool.exe`

### On Linux/Mac:
You can build, but it will create a Linux/Mac binary, not a Windows .exe. 
Use the GitHub Actions workflow for Windows builds.

## Troubleshooting

### Workflow Fails
- Check the Actions log for errors
- Common issues:
  - Missing dependencies in `requirements.txt`
  - Build script errors
  - PyInstaller compatibility issues

### Release Not Created
- Ensure the tag follows the pattern `v*.*.*`
- Check that GITHUB_TOKEN has permissions
- Verify the workflow file is in `.github/workflows/`

### .exe Not Attached
- Check the build step completed successfully
- Verify the path `dist/SuperDiagnosticTool.exe` is correct
- Check the upload-release-asset step logs

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **Major (X.0.0)**: Breaking changes, major features
- **Minor (1.X.0)**: New features, backward compatible
- **Patch (1.0.X)**: Bug fixes, security patches

## Security Notes

- Never commit API keys or secrets
- Review all changes before releasing
- Test the executable before announcing
- Update security documentation if needed

## Post-Release

After a successful release:
1. Test the download link
2. Update project documentation
3. Close related GitHub issues
4. Announce the release (if major)

## Quick Reference

```bash
# Complete release process
git add .
git commit -m "v1.0.2 - Description"
git push origin main
git tag -a v1.0.2 -m "Release notes"
git push origin v1.0.2

# Then wait for GitHub Actions to build and release
```

---

For questions or issues, open a GitHub issue or contact: hossam.guettaf@proton.me
