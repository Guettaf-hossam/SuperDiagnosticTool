import os
import sys
import platform
import json
import subprocess
import webbrowser
import time
from datetime import datetime
import ctypes
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- Auto-Install Dependencies ---
REQUIRED_LIBS = ["psutil", "google-generativeai", "rich"]
def install_libs():
    for lib in REQUIRED_LIBS:
        try:
            # Handle package name differences (google-generativeai is imported as google.generativeai)
            import_name = "google.generativeai" if lib == "google-generativeai" else lib
            if lib == "rich": import_name = "rich"
            if lib == "psutil": import_name = "psutil"
            
            __import__(import_name)
        except ImportError:
            print(f"Installing missing component: {lib}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

install_libs()

# Imports
import psutil
import google.generativeai as genai
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich.table import Table
from rich import box

# ============ CONFIGURATION ============
CACHE_DIR = os.path.join(os.getcwd(), "AI_Reports")
GEMINI_MODEL = "gemini-2.0-flash" 
console = Console()

# ============ CORE ENGINE ============

class SystemBrain:
    @staticmethod
    def run_powershell(cmd):
        try:
            # Using specific encoding handling to avoid errors
            full_cmd = f'{cmd}'
            result = subprocess.run(["powershell", "-Command", full_cmd], 
                                  capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return result.stdout.strip()
        except Exception:
            return "N/A"

    @staticmethod
    def get_api_key():
        key = os.getenv("GEMINI_API_KEY")
        if key: return key
        
        key_file = "gemini.key"
        if os.path.exists(key_file):
            with open(key_file, "r") as f: return f.read().strip()
            
        console.clear()
        console.print(Panel.fit("[bold yellow]⚠ Access Key Required[/bold yellow]", border_style="red"))
        key = Prompt.ask("[bold cyan]Enter Google Gemini API Key[/bold cyan]", password=True)
        with open(key_file, "w") as f: f.write(key)
        return key

# ============ SCANNING TASKS ============

def scan_context_system():
    return "System Core", {
        "OS": f"{platform.system()} {platform.release()} {platform.version()}",
        "Boot Time": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
        "CPU Context": f"{psutil.cpu_count(logical=False)} Cores / {psutil.cpu_count(logical=True)} Threads",
        "Battery": SystemBrain.run_powershell("Get-CimInstance -ClassName Win32_Battery | Select-Object -Property EstimatedChargeRemaining, BatteryStatus")
    }

def scan_performance():
    return "Performance Metrics", {
        "CPU Load": psutil.cpu_percent(interval=1, percpu=True),
        "RAM Usage": f"{psutil.virtual_memory().percent}% used of {round(psutil.virtual_memory().total / (1024**3), 1)} GB",
        "Top RAM Hogs": [p.info for p in sorted(psutil.process_iter(['name', 'memory_percent']), key=lambda p: p.info['memory_percent'], reverse=True)[:5]]
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
    # Fetching critical errors
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

# ============ REPORT GENERATOR ============

def generate_super_html(data, ai_analysis, user_problem):
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

# ============ MAIN EXECUTION FLOW ============

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    # 1. Admin Check & Auto-Elevation
    if not is_admin():
        # Re-run the program with admin rights
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

    os.system('cls' if os.name == 'nt' else 'clear')
    
    console.print(Panel.fit(
        "[bold cyan]AI WINDOWS DIAGNOSTIC TOOL[/bold cyan]\n[dim]v1.0[/dim]\n[bold yellow]Created by Knight[/bold yellow]", 
        subtitle="Powered by Google Gemini AI", border_style="cyan"
    ))

    api_key = SystemBrain.get_api_key()
    
    console.print("\n[bold green]?[/bold green] [bold white]Describe the problem you are facing.[/bold white]")
    user_problem = Prompt.ask("[bold cyan]>[/bold cyan] ", default="General Health Check")

    # 2. Scan Modes
    console.print("\n[bold yellow]Select Scan Mode:[/bold yellow]")
    console.print("[1] [bold green]Quick Scan[/bold green] (CPU, RAM, Basic Info)")
    console.print("[2] [bold red]Deep Scan[/bold red] (Full System, Network, Logs, Security, Bluetooth)")
    console.print("[3] [bold magenta]COMPLETE SYSTEM SCAN[/bold magenta] (Everything + Disk Health, GPU, Startup Apps)")
    mode = Prompt.ask("[bold cyan]>[/bold cyan] ", choices=["1", "2", "3"], default="3")

    if mode == "1":
        tasks = [scan_context_system, scan_performance]
        console.print("[dim]Running Quick Scan...[/dim]")
    elif mode == "2":
        tasks = [scan_context_system, scan_performance, scan_network_deep, scan_security_integrity, scan_event_logs, scan_bluetooth]
        console.print("[dim]Running Deep Scan...[/dim]")
    else:
        tasks = [scan_context_system, scan_performance, scan_network_deep, scan_security_integrity, scan_event_logs, scan_bluetooth, scan_disk_health, scan_gpu, scan_startup_apps]
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
    You are an Elite Tier-3 Windows Systems Engineer.
    USER COMPLAINT: "{user_problem}"
    SYSTEM TELEMETRY DATA:
    {json.dumps(collected_data, default=str)}
    
    YOUR MISSION:
    1. Correlate the "User Complaint" with the provided "Telemetry Data".
    2. Provide technical steps (PowerShell/CMD/Settings).
    3. If Bluetooth or Wi-Fi is mentioned, assume hardware troubleshooting steps are needed if logs are clean.
    
    OUTPUT FORMAT (HTML-Ready):
    <h3>Diagnosis</h3>
    <h3>Step-by-Step Fix</h3>
    <h3>Expert Advice</h3>
    """
    
    try:
        # FIXED: Changed 'binary' to 'dots' to prevent crash
        with console.status("[bold green]Analyzing patterns and logic...", spinner="dots"):
            # 3. Offline Mode / Graceful Failure
            try:
                response = model.generate_content(prompt)
                ai_analysis = response.text.replace("```html", "").replace("```", "").strip()
            except Exception as net_err:
                ai_analysis = f"<h3>⚠ AI Analysis Unavailable</h3><p>Could not connect to Gemini AI Server. Error: {str(net_err)}</p><p>Please check your internet connection. The raw data below is still valid.</p>"
                console.print(f"[bold red]AI Connection Failed:[/bold red] {net_err}")
            
        html_content = generate_super_html(collected_data, ai_analysis, user_problem)
        
        if not os.path.exists(CACHE_DIR): os.makedirs(CACHE_DIR)
        report_file = os.path.join(CACHE_DIR, f"Diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        console.print(Panel(f"[bold green]✔ MISSION ACCOMPLISHED[/bold green]\nReport generated: [underline]{report_file}[/underline]", border_style="green"))
        
        if Confirm.ask("Open the report now?"):
            webbrowser.open(f"file://{report_file}")
            
    except Exception as e:
        console.print(f"[bold red]CRITICAL FAILURE:[/bold red] {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()