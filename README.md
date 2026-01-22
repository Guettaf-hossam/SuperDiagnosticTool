# SuperDiagnosticTool

**SuperDiagnosticTool** is a standalone, AI-enhanced system telemetry utility for Windows environments. It leverages the Google Gemini API to analyze system performance metrics, event logs, and active processes, generating comprehensive HTML diagnostic reports and automated PowerShell remediation scripts.

![Home Screen](docs/console_start.png)

## Core Capabilities

### 1. Intelligent System Analysis
The tool aggregates data from multiple system layers (WMI, CIM, Event Viewer, and Performance Counters) and feeds this context into a large language model (LLM) to identify root causes of performance degradation or instability.

### 2. Security Process Audit
Includes a proprietary scanning module that inspects the running process list for anomalies.
- **Resource Monitoring:** Flags processes with disproportionate CPU or Memory usage.
- **Heuristic Analysis:** Identifies binaries running from suspect directories (e.g., AppData, Temp) often used by malware or PUPs.
- **Context Filtering:** Filters out known system services to focus on user-space anomalies.

### 3. Automated Remediation
Beyond diagnosis, the tool generates safe, non-destructive PowerShell scripts to address identified issues immediately.
- **Process Management:** Terminates resource-hogging background tasks.
- **System Maintenance:** Clears temporary directories and prefetch cache.
- **Service Recovery:** Attempts to restart critical Windows services that have failed.

### 4. Telemetry Coverage
- **Kernel/OS:** Version, uptime, battery health.
- **Resources:** CPU load per core, memory allocation, swapping.
- **Network:** Active interfaces, DNS configuration, latency checks.
- **Storage:** Drive health (S.M.A.R.T. status) and partition usage.
- **Security:** Antivirus status, firewall profiles, recent patches.

## Usage Guide

### Prerequisites
- Windows 10 or Windows 11
- Active Internet Connection (required for API analysis)
- Google Gemini API Key (Gemini 2.5 Flash supported)

### Installation
1. Download the latest `SuperDiagnosticTool.exe` from the Release section.
2. Place the executable in a preferred directory.
3. Right-click and select **Run as Administrator** (Required for WMI/Event Log access).

### Configuration
On first launch, you will be prompted to enter your Gemini API Key. This is stored locally in `gemini.key`.
To verify or reset your key, select Option 4 from the main menu.

### Operational Modes
- **Mode 1 (Quick Scan):** Rapid assessment of CPU/RAM load and basic OS stats.
- **Mode 2 (Deep Scan):** Detailed analysis including Network, Event Logs, and Security/Process Audit.
- **Mode 3 (Complete Scan):** Full system audit including Disk Health, GPU analytics, and Startup items.

## Architecture
- **Language:** Python 3.x
- **Libraries:** `psutil` (System Interface), `rich` (Console UI), `google-generativeai` (LLM Interface).
- **Build System:** PyInstaller (Single-file executable generation).

## Disclaimer
This tool is provided "as is" without warranty of any kind. While the remediation scripts are designed to be non-destructive, always review the generated script before execution. The author is not responsible for any system changes made by the automated scripts.

---
Copyright © 2026 Knight. All Rights Reserved.
