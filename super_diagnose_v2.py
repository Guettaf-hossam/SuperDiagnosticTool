import os
import re
import sys
import platform
import json
import subprocess
import webbrowser
import time
from datetime import datetime
import ctypes
from concurrent.futures import ThreadPoolExecutor, as_completed

REQUIRED_LIBS = ["psutil", "google-generativeai", "rich"]

def install_libs():
    for lib in REQUIRED_LIBS:
        try:
            import_name = "google.generativeai" if lib == "google-generativeai" else lib
            if lib == "rich": import_name = "rich"
            if lib == "psutil": import_name = "psutil"
            __import__(import_name)
        except ImportError:
            print(f"Installing missing component: {lib}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

install_libs()

import psutil
import google.generativeai as genai
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich.table import Table
from rich import box

CACHE_DIR = os.path.join(os.getcwd(), "AI_Reports")
GEMINI_MODEL = "gemini-2.5-flash" 
console = Console()

class SystemBrain:
    """Core system utilities for PowerShell execution and API key management."""
    
    @staticmethod
    def run_powershell(cmd):
        try:
            result = subprocess.run(["powershell", "-Command", cmd], 
                                  capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return result.stdout.strip()
        except Exception:
            return "N/A"

    @staticmethod
    def validate_key(key):
        if not key: return False
        clean_key = key.strip()
        if len(clean_key) < 30: return False
        return True

    @staticmethod
    def get_api_key():
        key = os.getenv("GEMINI_API_KEY")
        if key: return key.strip()
        
        key_file = "gemini.key"
        if os.path.exists(key_file):
            try:
                with open(key_file, "r") as f: 
                    saved_key = f.read().strip()
                saved_key = re.sub(r'[^a-zA-Z0-9\-\._]', '', saved_key).strip()
                if SystemBrain.validate_key(saved_key):
                    return saved_key
            except: pass

        console.clear()
        console.print(Panel.fit("[bold yellow]⚠ Access Key Required[/bold yellow]", border_style="red"))
        console.print("[dim]Key input is visible to support Ctrl+V pasting.[/dim]")
        
        while True:
            console.print("\n[bold cyan]Enter Google Gemini API Key:[/bold cyan]")
            try:
                raw_input = input("> ").strip()
            except:
                return ""
            
            clean_key = re.sub(r'[^a-zA-Z0-9\-\._]', '', raw_input).strip()
            
            if SystemBrain.validate_key(clean_key):
                with open(key_file, "w") as f: f.write(clean_key)
                console.print("[bold green]✔ Key accepted![/bold green]")
                return clean_key
            else:
                console.print(f"[bold red]✘ Invalid Key ({len(clean_key)} chars). Try again.[/bold red]")

    @staticmethod
    def reset_api_key():
        if os.path.exists("gemini.key"): os.remove("gemini.key")
        os.environ.pop("GEMINI_API_KEY", None)
        console.print("[bold green]API Key reset![/bold green]")
        return SystemBrain.get_api_key()


def scan_context_system():
    """Scan core system information and hardware context."""
    system_data = {}
    
    try:
        system_data["OS"] = f"{platform.system()} {platform.release()} {platform.version()}"
    except:
        system_data["OS"] = "Unknown"
    
    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        system_data["Boot Time"] = boot_time
    except:
        system_data["Boot Time"] = "N/A"
    
    try:
        physical_cores = psutil.cpu_count(logical=False) or "N/A"
        logical_cores = psutil.cpu_count(logical=True) or "N/A"
        system_data["CPU Context"] = f"{physical_cores} Cores / {logical_cores} Threads"
    except:
        system_data["CPU Context"] = "N/A"
    
    try:
        battery_info = SystemBrain.run_powershell("Get-CimInstance -ClassName Win32_Battery | Select-Object -Property EstimatedChargeRemaining, BatteryStatus")
        system_data["Battery"] = battery_info if battery_info and battery_info != "N/A" else "No Battery Detected"
    except:
        system_data["Battery"] = "No Battery Detected"
    
    return "System Core", system_data

def scan_performance():
    """Scan system performance metrics including CPU and memory usage."""
    
    cpu_data = {}
    mem_data = {}
    
    try:
        cpu_percent_overall = psutil.cpu_percent(interval=0.5)
        cpu_data["Overall Usage"] = f"{cpu_percent_overall}%"
    except:
        cpu_data["Overall Usage"] = "N/A"
    
    try:
        cpu_percent_per_core = psutil.cpu_percent(interval=0.3, percpu=True)
        core_count = len(cpu_percent_per_core)
        
        if core_count <= 8:
            cpu_data["Per-Core Usage"] = cpu_percent_per_core
        else:
            avg_usage = sum(cpu_percent_per_core) / core_count
            cpu_data["Average Core Usage"] = f"{avg_usage:.1f}%"
            cpu_data["Core Count"] = f"{core_count} cores"
    except:
        cpu_data["Per-Core Usage"] = "N/A"
    
    try:
        cpu_count_physical = psutil.cpu_count(logical=False) or "N/A"
        cpu_count_logical = psutil.cpu_count(logical=True) or "N/A"
        cpu_data["Cores"] = f"{cpu_count_physical} Physical / {cpu_count_logical} Logical"
    except:
        cpu_data["Cores"] = "N/A"
    
    try:
        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            cpu_data["Frequency"] = f"Current: {cpu_freq.current:.0f} MHz | Min: {cpu_freq.min:.0f} MHz | Max: {cpu_freq.max:.0f} MHz"
        else:
            cpu_data["Frequency"] = "Not Supported"
    except:
        cpu_data["Frequency"] = "Not Supported"
    
    try:
        mem = psutil.virtual_memory()
        mem_data["Total"] = f"{mem.total / (1024**3):.1f} GB"
        mem_data["Available"] = f"{mem.available / (1024**3):.1f} GB"
        mem_data["Used"] = f"{mem.used / (1024**3):.1f} GB ({mem.percent}%)"
    except:
        mem_data["Memory"] = "N/A"
    
    try:
        swap = psutil.swap_memory()
        if swap.total > 0:
            mem_data["Swap Used"] = f"{swap.used / (1024**3):.1f} GB ({swap.percent}%)"
        else:
            mem_data["Swap Used"] = "No Swap Configured"
    except:
        mem_data["Swap Used"] = "N/A"
    
    top_processes = []
    try:
        top_processes = [
            p.info for p in sorted(
                psutil.process_iter(['name', 'memory_percent']), 
                key=lambda p: p.info.get('memory_percent', 0), 
                reverse=True
            )[:5]
        ]
    except:
        top_processes = [{"name": "Unable to retrieve", "memory_percent": 0}]
    
    return "Performance Metrics", {
        "CPU": cpu_data,
        "Memory": mem_data,
        "Top RAM Consumers": top_processes
    }

def scan_network_deep():
    return "Network Intelligence", {
        "Active Interfaces": SystemBrain.run_powershell("Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object Name, InterfaceDescription, LinkSpeed"),
        "DNS Config": SystemBrain.run_powershell("Get-DnsClientServerAddress | Where-Object ServerAddresses -ne $null | Select-Object InterfaceAlias, ServerAddresses"),
        "Wi-Fi Signal": SystemBrain.run_powershell("netsh wlan show interfaces | Select-String 'Signal'"),
        "Ping Test (Google)": SystemBrain.run_powershell("Test-Connection -ComputerName 8.8.8.8 -Count 1 -Quiet")
    }

def scan_security_integrity():
    return "Security Integrity", {
        "Antivirus": SystemBrain.run_powershell("Get-MpComputerStatus | Select-Object AntivirusEnabled, RealTimeProtectionEnabled, DefenderSignaturesOutOfDate"),
        "Firewall Profiles": SystemBrain.run_powershell("Get-NetFirewallProfile | Select-Object Name, Enabled"),
        "Last Updates": SystemBrain.run_powershell("Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 5 HotFixID, InstalledOn")
    }

def scan_event_logs():
    cmd = "Get-WinEvent -FilterHashtable @{LogName='System';Level=1,2;StartTime=(Get-Date).AddHours(-24)} -MaxEvents 15 -ErrorAction SilentlyContinue | Select-Object TimeCreated, Message"
    return "Critical Events", SystemBrain.run_powershell(cmd)

def scan_bluetooth():
    return "Bluetooth Status", {
        "Devices": SystemBrain.run_powershell("Get-PnpDevice -Class Bluetooth | Select-Object FriendlyName, Status, Class | Sort-Object Status"),
        "Radio State": SystemBrain.run_powershell("Get-NetAdapter | Where-Object InterfaceDescription -like '*Bluetooth*' | Select-Object Name, Status")
    }

def scan_disk_health():
    return "Disk Health & Storage", {
        "Physical Drives (SMART)": SystemBrain.run_powershell("Get-PhysicalDisk | Select-Object FriendlyName, MediaType, HealthStatus, OperationalStatus, Size"),
        "Partitions": SystemBrain.run_powershell("Get-Volume | Where-Object DriveLetter -ne $null | Select-Object DriveLetter, FileSystemLabel, SizeRemaining, Size")
    }

def scan_gpu():
    return "Graphics & GPU", {
        "Controllers": SystemBrain.run_powershell("Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion, VideoProcessor, AdapterRAM")
    }

def scan_startup_apps():
    return "Startup & Services", {
        "Startup Apps": SystemBrain.run_powershell("Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location, User"),
        "Failed Services": SystemBrain.run_powershell("Get-Service | Where-Object {$_.Status -eq 'Stopped' -and $_.StartType -eq 'Automatic'} | Select-Object Name, DisplayName")
    }

def scan_suspicious_processes():
    """Scan for potentially suspicious processes based on resource usage and location."""
    suspicious_list = []
    
    WHITELIST = [
        "Antigravity.exe", "SuperDiagnosticTool.exe", "super_diagnose_v2.exe", 
        "python.exe", "git.exe", "GitHubDesktop.exe", "ssh-agent.exe"
    ]
    
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'username', 'cpu_percent', 'memory_info']):
        try:
            pinfo = proc.info
            name = pinfo['name']
            
            if name in WHITELIST:
                continue
                
            is_resource_heavy = (pinfo['cpu_percent'] > 1.0) or (pinfo['memory_info'].rss > 100 * 1024 * 1024)
            exe_path = pinfo['exe'] or ""
            is_user_path = "Users" in exe_path and "Windows" not in exe_path
            
            if is_resource_heavy or is_user_path:
                suspicious_list.append({
                    "Name": name,
                    "PID": pinfo['pid'],
                    "Path": exe_path,
                    "User": pinfo['username'],
                    "CPU%": pinfo['cpu_percent'],
                    "Mem(MB)": round(pinfo['memory_info'].rss / (1024 * 1024), 2)
                })
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    suspicious_list.sort(key=lambda x: x['CPU%'], reverse=True)
    return "Suspicious Process Audit", suspicious_list[:30]


def generate_super_html(data, ai_analysis, user_problem):
    """Generate a professional HTML diagnostic report with AI analysis."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    css = """
    :root { --bg: #0d1117; --card: #161b22; --text: #c9d1d9; --accent: #58a6ff; --danger: #f85149; --success: #3fb950; }
    body { font-family: 'Segoe UI', system-ui, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; }
    .container { max-width: 1200px; margin: 0 auto; }
    h1 { border-bottom: 2px solid var(--accent); padding-bottom: 10px; color: var(--accent); text-transform: uppercase; letter-spacing: 2px; }
    .status-bar { display: flex; gap: 20px; margin-bottom: 30px; }
    .stat-card { flex: 1; background: var(--card); padding: 20px; border-radius: 8px; border: 1px solid #30363d; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .stat-card h3 { margin: 0; font-size: 0.9rem; color: #8b949e; }
    .stat-card .value { font-size: 2rem; font-weight: bold; margin-top: 10px; }
    .problem-box { background: rgba(248, 81, 73, 0.1); border-left: 5px solid var(--danger); padding: 20px; margin-bottom: 30px; }
    .ai-analysis { background: linear-gradient(145deg, #1f2428, #161b22); padding: 30px; border-radius: 12px; border: 1px solid var(--accent); margin-bottom: 30px; position: relative; overflow: hidden; }
    .ai-analysis::before { content: "AI INSIGHTS"; position: absolute; top: 0; right: 0; background: var(--accent); color: #000; padding: 5px 15px; font-weight: bold; font-size: 0.8rem; border-bottom-left-radius: 10px; }
    .raw-data { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }
    .data-panel { background: var(--card); padding: 20px; border-radius: 8px; border: 1px solid #30363d; height: 300px; overflow-y: auto; }
    .data-panel h4 { color: var(--success); border-bottom: 1px solid #30363d; padding-bottom: 10px; margin-top: 0; }
    pre { white-space: pre-wrap; font-family: 'Consolas', monospace; font-size: 0.85rem; color: #8b949e; }
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 4px; }
    """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Diagnostic Core | {timestamp}</title>
        <style>{css}</style>
    </head>
    <body>
        <div class="container">
            <h1>System Diagnostic Core <span style="font-size:0.5em; float:right; color:var(--text)">{timestamp}</span></h1>
            
            <div class="problem-box">
                <h3 style="margin-top:0; color:var(--danger)">REPORTED ISSUE</h3>
                <p>"{user_problem}"</p>
            </div>

            <div class="status-bar">
                <div class="stat-card">
                    <h3>CPU CORES</h3>
                    <div class="value" style="color:var(--accent)">{psutil.cpu_count()}</div>
                </div>
                <div class="stat-card">
                    <h3>MEMORY LOAD</h3>
                    <div class="value" style="color: { 'var(--danger)' if psutil.virtual_memory().percent > 85 else 'var(--success)' }">
                        {psutil.virtual_memory().percent}%
                    </div>
                </div>
                <div class="stat-card">
                    <h3>OS PLATFORM</h3>
                    <div class="value" style="font-size: 1.2rem; margin-top:15px">{platform.system()} {platform.release()}</div>
                </div>
            </div>

            <div class="ai-analysis">
                <h2>🤖 Intelligent Analysis & Fixes</h2>
                <div style="line-height: 1.6; font-size: 1.1rem;">
                    {ai_analysis.replace(chr(10), '<br>')}
                </div>
            </div>

            <div class="raw-data">
    """
    
    for key, value in data.items():
        formatted_val = json.dumps(value, indent=2, default=str).replace('"', '')
        html += f"""
        <div class="data-panel">
            <h4>{key.upper()}</h4>
            <pre>{formatted_val}</pre>
        </div>
        """

    html += """
            </div>
            <div style="text-align:center; margin-top:50px; color:#555; font-size:0.8rem;">
                GENERATED BY SUPER DIAGNOSTIC TOOL v1.0<br>
                <span style="color:var(--accent)">Developed by Knight</span> | <a href="mailto:hossam.guettaf@proton.me" style="color:#555; text-decoration:none">hossam.guettaf@proton.me</a>
            </div>
        </div>
    </body>
    </html>
    """
    return html


def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    """Main execution flow for the diagnostic tool."""
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

    os.system('cls' if os.name == 'nt' else 'clear')
    
    console.print(Panel.fit(
        "[bold cyan]AI WINDOWS DIAGNOSTIC TOOL[/bold cyan]\n[dim]v1.0[/dim]\n[bold yellow]Created by Knight[/bold yellow]", 
        subtitle="Powered by Google Gemini AI", border_style="cyan"
    ))

    api_key = SystemBrain.get_api_key()
    if api_key:
        masked_key = api_key[:5] + "*" * (len(api_key) - 5)
        console.print(f"[dim]Loaded API Key: {masked_key}[/dim]")
    
    console.print("\n[bold green]?[/bold green] [bold white]Describe the problem you are facing.[/bold white]")
    user_problem = Prompt.ask("[bold cyan]>[/bold cyan] ", default="General Health Check")

    console.print("\n[bold yellow]Select Scan Mode:[/bold yellow]")
    console.print("[1] [bold green]Quick Scan[/bold green] (CPU, RAM, Basic Info)")
    console.print("[2] [bold red]Deep Scan[/bold red] (Full System, Network, Logs, Security, Bluetooth)")
    console.print("[3] [bold magenta]COMPLETE SYSTEM SCAN[/bold magenta] (Everything + Disk Health, GPU, Startup Apps)")
    console.print("[4] [bold white]Update API Key[/bold white]")
    mode = Prompt.ask("[bold cyan]>[/bold cyan] ", choices=["1", "2", "3", "4"], default="3")

    if mode == "4":
        api_key = SystemBrain.reset_api_key()
        console.print("\n[bold green]Key Updated Successfully![/bold green]")
        console.print("\n[bold yellow]Select Scan Mode:[/bold yellow]")
        console.print("[1] [bold green]Quick Scan[/bold green] (CPU, RAM, Basic Info)")
        console.print("[2] [bold red]Deep Scan[/bold red] (Full System, Network, Logs, Security, Bluetooth)")
        console.print("[3] [bold magenta]COMPLETE SYSTEM SCAN[/bold magenta] (Everything + Disk Health, GPU, Startup Apps)")
        mode = Prompt.ask("[bold cyan]>[/bold cyan] ", choices=["1", "2", "3"], default="3")

    if mode == "1":
        tasks = [scan_context_system, scan_performance]
        console.print("[dim]Running Quick Scan...[/dim]")
    elif mode == "2":
        tasks = [scan_context_system, scan_performance, scan_network_deep, scan_security_integrity, scan_event_logs, scan_bluetooth, scan_suspicious_processes]
        console.print("[dim]Running Deep Scan...[/dim]")
    else:
        tasks = [scan_context_system, scan_performance, scan_network_deep, scan_security_integrity, scan_event_logs, scan_bluetooth, scan_disk_health, scan_gpu, scan_startup_apps, scan_suspicious_processes]
        console.print("[bold magenta]INITIATING COMPLETE SYSTEM SCAN...[/bold magenta]")
    collected_data = {"User Reported Issue": user_problem}
    
    print()
    with Progress(
        SpinnerColumn("dots", style="bold magenta"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None, complete_style="green", finished_style="green"),
        console=console
    ) as progress:
        
        main_task = progress.add_task("[cyan]Scanning System Layers...", total=len(tasks))
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_task = {executor.submit(t): t.__name__ for t in tasks}
            
            for future in as_completed(future_to_task):
                name = future_to_task[future]
                try:
                    category, data = future.result()
                    collected_data[category] = data
                    progress.advance(main_task)
                except Exception as e:
                    collected_data[name] = str(e)

    console.print(Panel("[bold yellow]Transmitting telemetry to Neural Core...[/bold yellow]", border_style="yellow"))
    

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_MODEL)
    
    prompt = f"""
    ROLE: Senior Windows Systems Engineer & Security Analyst.
    CONTEXT: User is reporting system issues. Telemetry data is attached.
    
    TASK:
    1. ANALYZE: Correlate user report with system metrics.
    2. AUDIT: Review process list for anomalies (resource leaks, unknown binaries, potential malware).
    3. REPORT: Generate a technical diagnosis in HTML format.
    4. REMEDIATION: Generate a PowerShell script to resolve identified issues.
       
       POWERSHELL SCRIPT REQUIREMENTS:
       - Start with admin privilege check (exit if not admin)
       - Use 'Write-Host' for all logging with color coding
       - When using variables followed by colons, wrap in $(): e.g., "$($path):" not "$path:"
       - For Intel services (esrv_svc, SurSvc, esrv): Check existence with Get-Service -ErrorAction SilentlyContinue first
       - All service operations must use -ErrorAction SilentlyContinue
       - Operations must be non-destructive (no data loss)
       - Include Try/Catch blocks for critical operations
    
    OUTPUT STRUCTURE:
    
    [ANALYSIS_START]
    <h3>Maintenance Report: Operations Completed</h3>
    <p>List completed actions using [FIXED], [CLEANED], [DISABLED] tags in past tense.</p>
    <ul>
        <li>[FIXED] Disabled crashing Intel service (esrv_svc)</li>
        <li>[CLEANED] Removed temporary files from system cache</li>
    </ul>
    
    <h3>Manual Attention Required</h3>
    <p>Items that require user intervention or cannot be automated.</p>
    <ul>
        <li>Update graphics driver manually from manufacturer website</li>
    </ul>
    [ANALYSIS_END]
    
    [FIX_START]
    # Admin privilege check
    if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {{
        Write-Host "ERROR: This script requires Administrator privileges" -ForegroundColor Red
        exit 1
    }}
    
    Write-Host "Initializing remediation protocols..." -ForegroundColor Cyan
    
    # Example: Intel service handling
    $intelServices = @('esrv_svc', 'SurSvc', 'esrv')
    foreach ($svc in $intelServices) {{
        $service = Get-Service -Name $svc -ErrorAction SilentlyContinue
        if ($service) {{
            Write-Host "Found Intel service: $($svc)" -ForegroundColor Yellow
            Try {{
                Stop-Service -Name $svc -Force -ErrorAction SilentlyContinue
                Set-Service -Name $svc -StartupType Disabled -ErrorAction SilentlyContinue
                Write-Host "Disabled: $($svc)" -ForegroundColor Green
            }} Catch {{
                Write-Host "Could not modify: $($svc)" -ForegroundColor Red
            }}
        }}
    }}
    [FIX_END]
    
    USER COMPLAINT: "{user_problem}"
    TELEMETRY:
    {json.dumps(collected_data, default=str)}
    """
    
    try:
        with console.status("Processing telemetry logic...", spinner="dots"):
            max_retries = 3
            raw_response = ""
            for attempt in range(max_retries):
                try:
                    response = model.generate_content(prompt)
                    raw_response = response.text
                    break 
                except Exception as e:
                    if "429" in str(e) or "Resource exhausted" in str(e):
                        if attempt < max_retries - 1:
                            console.print(f"[yellow]API quota limit reached. Retrying in 4s... ({attempt+1}/{max_retries})[/yellow]")
                            time.sleep(4)
                            continue
                    
                    raw_response = f"[ANALYSIS_START]<h3>Analysis Unavailable</h3><p>API Error: {str(e)}</p>[ANALYSIS_END]"
                    break
        
        ai_analysis = ""
        fix_script = ""
        
        if "[ANALYSIS_START]" in raw_response:
            ai_analysis = raw_response.split("[ANALYSIS_START]")[1].split("[ANALYSIS_END]")[0].strip()
        else:
            ai_analysis = raw_response
            
        if "[FIX_START]" in raw_response:
            fix_script = raw_response.split("[FIX_START]")[1].split("[FIX_END]")[0].strip()
            fix_script = fix_script.replace("```powershell", "").replace("```", "").strip()
            
            fix_script = re.sub(r'\$(?!env\b)(\w+):', r'$(\1):', fix_script)
            fix_script = re.sub(r'\$_([:])', r'$($_)\1', fix_script)
        
        html_content = generate_super_html(collected_data, ai_analysis, user_problem)
        
        if not os.path.exists(CACHE_DIR): os.makedirs(CACHE_DIR)
        report_file = os.path.join(CACHE_DIR, f"Diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        console.print(Panel(f"[bold green]ANALYSIS COMPLETE[/bold green]\nReport: [underline]{report_file}[/underline]", border_style="green"))
        
        if fix_script and len(fix_script) > 10:
            console.print("\n")
            console.print(Panel.fit("[bold magenta]AUTOMATED REMEDIATION SYSTEM[/bold magenta]", border_style="magenta"))
            console.print("[dim]A remediation script has been generated based on the analysis:[/dim]\n")
            
            console.print(Panel(fix_script, title="PowerShell Remediation Script", style="white on black"))
            
            if Confirm.ask("[bold yellow]EXECUTE REMEDIATION SCRIPT?[/bold yellow]"):
                console.print("\n[bold green]Executing...[/bold green]")
                
                script_path = os.path.join(CACHE_DIR, "remediation.ps1")
                with open(script_path, "w") as f:
                    f.write(fix_script)
                
                try:
                    p = subprocess.run(
                        ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path],
                        capture_output=False 
                    )
                    
                    if p.returncode == 0:
                        console.print("\n[bold green]REMEDIATION SUCCESSFUL[/bold green]")
                    else:
                        console.print(f"\n[bold red]REMEDIATION COMPLETED WITH WARNINGS (Code {p.returncode})[/bold red]")
                         
                except Exception as e:
                     console.print(f"[bold red]Execution Error:[/bold red] {e}")
                
                if Confirm.ask("\nOpen detailed report?"):
                    webbrowser.open(f"file://{report_file}")
            else:
                console.print("[dim]Script execution skipped.[/dim]")
                
                if Confirm.ask("\nOpen detailed report?"):
                    webbrowser.open(f"file://{report_file}")
    except Exception as e:
        console.print(f"[bold red]SYSTEM ERROR:[/bold red] {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()