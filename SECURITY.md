# Security Notice

## API Key Protection

**IMPORTANT:** This repository does NOT include any API keys.

### First-Time Setup

When you run `SuperDiagnosticTool.exe` for the first time, you will be prompted to enter your Google Gemini API key.

### How to Get Your API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key

### Key Storage

Your API key will be stored locally in a file called `gemini.key` in the same directory as the executable. This file is:
- ✅ **Local only** - Never uploaded to GitHub
- ✅ **Gitignored** - Protected from accidental commits
- ✅ **User-specific** - Each user enters their own key

### Security Best Practices

- **Never share your API key** with others
- **Never commit** `gemini.key` to version control
- **Regenerate your key** if you suspect it has been compromised
- **Keep your key private** - It's linked to your Google account

---

**Note:** The developer's personal API key is NOT included in this repository or any releases.
