# SuperDiagnosticTool

<p align="center">
  <img src="docs/icon.png" alt="SuperDiagnosticTool Icon" width="200"/>
</p>

**AI-Powered Windows Diagnostic & Self-Healing Tool**

SuperDiagnosticTool is an intelligent system diagnostic utility that combines real-time hardware telemetry with Google Gemini AI to analyze, diagnose, and automatically remediate Windows system issues. Built with a safety-first architecture, it provides production-grade diagnostics for any Windows configuration.

---

## Key Features

### Universal Hardware Support
- **Dynamic Scaling:** Automatically adapts to any CPU configuration (1-128+ cores)
- **Hardware-Agnostic Logic:** Works seamlessly on legacy systems (Intel Pentium) to high-end workstations (AMD Threadripper, Intel Xeon)
- **Graceful Fallbacks:** Safe handling of unsupported features (CPU frequency, battery detection, swap memory)
- **Low-Spec Optimized:** Lightweight execution prevents system lags even on resource-constrained hardware

### Intelligent AI Analysis
- **Google Gemini Integration:** Advanced AI-powered system analysis and diagnostics
- **Context-Aware Recommendations:** Correlates user-reported issues with system telemetry
- **Security Auditing:** Scans for suspicious processes, resource leaks, and potential malware
- **Post-Fix Verification:** Generates completion reports showing what was fixed vs. what requires manual attention

### Safety-First Architecture
- **Admin Privilege Verification:** All remediation scripts include elevation checks
- **PowerShell Variable Sanitization:** Regex-based escaping prevents `InvalidVariableReferenceWithDrive` errors while preserving `$env:` variables
- **Service Safety Checks:** Verifies service existence before attempting stop/disable operations
- **Non-Destructive Operations:** All automated fixes are designed to prevent data loss
- **Error Handling:** Comprehensive try-catch blocks with `-ErrorAction SilentlyContinue` safeguards

### Comprehensive System Scanning
- **Performance Metrics:** CPU usage (overall + per-core), memory breakdown, top resource consumers
- **Network Intelligence:** Active interfaces, DNS configuration, Wi-Fi signal strength, connectivity tests
- **Security Integrity:** Antivirus status, firewall profiles, Windows Update history
- **Hardware Health:** Disk SMART status, GPU information, battery status (laptops)
- **System Services:** Startup applications, failed services, critical event logs
- **Process Auditing:** Identifies suspicious processes based on resource usage and location

### Human-Centric Reporting
- **Professional HTML Reports:** Dark-themed, responsive diagnostic reports with visual metrics
- **Past-Tense Completion Language:** Reports use `[FIXED]`, `[CLEANED]`, `[DISABLED]` tags to show completed actions
- **Manual Attention Section:** Clearly separates automated fixes from items requiring user intervention
- **Timestamped Archives:** All reports saved to `AI_Reports/` directory for historical tracking

---

## Installation

### Prerequisites
- **Operating System:** Windows 10/11 (Administrator privileges required)
- **Python:** 3.8 or higher
- **Google Gemini API Key:** [Get your free API key](https://makersuite.google.com/app/apikey)

### Dependencies
Install required Python packages:

```bash
pip install psutil google-generativeai rich
```

Or use the auto-installer (dependencies are installed automatically on first run).

---

## Usage

### 1. API Key Setup

**Option A: Environment Variable (Recommended)**
```bash
set GEMINI_API_KEY=your_api_key_here
```

**Option B: Key File**
Create a `gemini.key` file in the same directory as the script:
```
your_api_key_here
```

**Option C: Interactive Input**
The tool will prompt you to enter your API key on first run if not found.

### 2. Run the Tool

```bash
python super_diagnose_v2.py
```

The tool will automatically:
1. Request administrator privileges (UAC prompt)
2. Display the main menu
3. Prompt for problem description
4. Offer scan mode selection:
   - **Quick Scan:** CPU, RAM, basic info
   - **Deep Scan:** Full system, network, logs, security, Bluetooth
   - **Complete System Scan:** Everything + disk health, GPU, startup apps

### 3. Review Results

After scanning:
- **AI Analysis:** View intelligent diagnosis in the terminal
- **Remediation Script:** Review and optionally execute the generated PowerShell fix
- **HTML Report:** Open detailed diagnostic report in your browser

---

## Scan Modes

| Mode | Scans | Use Case |
|------|-------|----------|
| **Quick Scan** | CPU, RAM, Basic Info | Fast performance check |
| **Deep Scan** | System, Network, Security, Logs, Bluetooth, Processes | Comprehensive troubleshooting |
| **Complete Scan** | All of the above + Disk Health, GPU, Startup Apps | Full system audit |

---

## Example Workflow

```bash
# 1. Run the tool
python super_diagnose_v2.py

# 2. Describe your issue
> High CPU usage and slow performance

# 3. Select scan mode
> 3 (Complete System Scan)

# 4. Wait for AI analysis
[Scanning system layers...]
[Processing telemetry logic...]

# 5. Review remediation script
[PowerShell script displayed]
> Execute? (y/n)

# 6. View HTML report
> Open detailed report? (y/n)
```

---

## Architecture Highlights

### Production-Ready Code Quality
- **Clean Code Principles:** Minimal comments, professional docstrings, human-readable variable names
- **No Robotic Headers:** Removed AI-generated ASCII art and excessive section markers
- **Safety Checks:** Every hardware query wrapped in try-except with graceful fallbacks
- **Modular Design:** Separate functions for each diagnostic category

### PowerShell Script Generation
- **Admin Privilege Check:** Scripts verify elevation before executing
- **Variable Escaping:** Regex sanitization prevents syntax errors (`$path:` → `$($path):`)
- **Environment Variable Preservation:** `$env:TEMP` and `$env:PATH` remain untouched
- **Intel Service Handling:** Safe stop/disable for problematic services (esrv_svc, SurSvc, esrv)
- **Error Resilience:** All operations use `-ErrorAction SilentlyContinue`

### AI Prompt Engineering
- **Role-Based Prompting:** AI acts as "Senior Windows Systems Engineer & Security Analyst"
- **Structured Output:** Enforces `[ANALYSIS_START]` and `[FIX_START]` delimiters for parsing
- **Post-Fix Tone:** Reports use past-tense language to describe completed actions
- **Example Templates:** Provides PowerShell best practices directly in the prompt

---

## File Structure

```
SuperDiagnosticTool/
├── super_diagnose_v2.py    # Main diagnostic script
├── gemini.key              # API key file (optional)
├── AI_Reports/             # Generated HTML reports
│   └── Diagnosis_YYYYMMDD_HHMMSS.html
├── README.md               # This file
└── LICENSE                 # GPL-3.0 License
```

---

## Security & Privacy

- **No Data Collection:** All analysis happens locally; only system telemetry is sent to Gemini API
- **API Key Security:** Keys are sanitized and validated before use
- **Admin Transparency:** User must explicitly approve all remediation scripts
- **Non-Destructive:** No file deletion or registry modifications without user consent

---

## Troubleshooting

### "API Key Invalid" Error
- Verify your API key is correct and active
- Check for hidden characters or whitespace
- Ensure the key has Gemini API access enabled

### "Not Running as Administrator"
- Right-click the script and select "Run as Administrator"
- Or allow the UAC prompt when the tool auto-elevates

### "Module Not Found" Error
```bash
pip install --upgrade psutil google-generativeai rich
```

### PowerShell Script Fails
- Ensure you're running Windows PowerShell 5.1 or later
- Check that execution policy allows script execution
- Review the script in `AI_Reports/remediation.ps1` for errors

---

## Disclaimer

**IMPORTANT: System Modification Warning**

This tool generates and executes PowerShell scripts that modify system services, configurations, and settings. While designed with safety-first principles:

- **Always review** the generated PowerShell script before execution
- **Backup critical data** before running automated remediation
- **Test on non-production systems** first if possible
- **Understand the changes** being made to your system

The author is not responsible for any system damage, data loss, or unintended consequences resulting from the use of this tool. Use at your own risk.

---

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -m 'Add improvement'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Open a Pull Request

---

## License

This project is licensed under the **GNU General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

---

## Author

**Knight**  
Email: hossam.guettaf@proton.me

---

## Acknowledgments

- **Google Gemini AI** for intelligent system analysis
- **psutil** library for cross-platform system monitoring
- **Rich** library for beautiful terminal output

---

**Version:** 1.0  
**Last Updated:** January 2026
