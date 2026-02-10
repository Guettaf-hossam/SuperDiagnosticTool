# 🛡️ How to Fix "Unknown Publisher" Warning

Since this is a free, open-source tool, it doesn't have a $300/year corporate digital signature. However, you can make it trusted and safe.

## ✅ Option 1: Fast Fix (For You)
When you see the **"Windows protected your PC"** popup:
1. Click **"More info"**.
2. Click **"Run anyway"**.
3. Windows will remember this choice for this specific file.

## 🔐 Option 2: Establish Global Trust (Recommended)
To permanently stop this warning for **everyone** who downloads your tool, follow these steps:

### Step 1: Sign the Executable (Local Trust)
We have included a script to digitally sign the app with your name ("Hossam Guettaf - Open Source").
1. Open PowerShell as **Administrator**.
2. Run the trust setup script:
   ```powershell
   .\setup_trust.ps1
   ```
3. This will:
   - Create a self-signed certificate.
   - Sign `dist\SuperDiagnosticTool.exe`.
   - Install the certificate locally so your PC trusts it.

### Step 2: Submit to Microsoft (Global Trust)
This is the **most important** step. Microsoft provides a free service to analyze software and remove the SmartScreen warning.

1. Go to: **[Microsoft Security Intelligence - Submit a File](https://www.microsoft.com/en-us/wdsi/filesubmission)**
2. Select **"Home customer"** (no login required) or **"Software developer"** (requires Microsoft account, better for tracking).
3. Upload your signed `SuperDiagnosticTool.exe`.
4. Select **"Incorrectly detected as malware/malicious"** (since SmartScreen is blocking it).
5. In comments, write:
   > "This is an open-source system diagnostic tool for students. It is false-positive blocked by SmartScreen. Please analyze and whitelist."
6. **Wait:** Microsoft usually analyzes files within 2-24 hours. Once cleared, the "Unknown Publisher" warning will disappear for **everyone options** worldwide.

## ⚠️ Notes
- **Re-submission:** If you release a new version (v1.0.5, etc.), the file hash changes. You may need to submit the new `.exe` to Microsoft again.
 - **Open Source Transparency:** Your code is open on GitHub. This is your best proof of safety!
