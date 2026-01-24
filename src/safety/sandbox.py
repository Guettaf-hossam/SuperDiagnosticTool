"""Sandbox executor for safe PowerShell script execution with monitoring."""

import subprocess
import tempfile
import os
from pathlib import Path
from typing import Tuple, Optional


class SandboxExecutor:
    """Execute PowerShell scripts with monitoring and safety limits."""
    
    def __init__(self, script: str):
        """
        Initialize sandbox executor.
        
        Args:
            script: PowerShell script to execute
        """
        self.script = script
        self.execution_log = []
        
    def execute_with_monitoring(self, timeout: int = 300) -> Tuple[bool, str, str]:
        """
        Execute script with real-time monitoring and safety limits.
        
        Args:
            timeout: Maximum execution time in seconds
            
        Returns:
            (success, stdout, stderr): Execution results
        """
        script_path = None
        
        try:
            # Create temporary script file with monitoring wrapper
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.ps1',
                delete=False,
                encoding='utf-8'
            ) as f:
                wrapped_script = self._wrap_with_monitoring(self.script)
                f.write(wrapped_script)
                script_path = f.name
            
            # Execute with constraints
            result = subprocess.run(
                [
                    "powershell",
                    "-ExecutionPolicy", "Bypass",
                    "-NoProfile",
                    "-NonInteractive",
                    "-File", script_path
                ],
                capture_output=True,
                text=True,
                timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            success = result.returncode == 0
            return success, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return False, "", f"Script execution timeout after {timeout} seconds"
        except Exception as e:
            return False, "", f"Execution error: {str(e)}"
        finally:
            # Cleanup temporary file
            if script_path and os.path.exists(script_path):
                try:
                    os.unlink(script_path)
                except:
                    pass
    
    def _wrap_with_monitoring(self, script: str) -> str:
        """
        Wrap script with monitoring and safety code.
        
        Args:
            script: Original PowerShell script
            
        Returns:
            Wrapped script with monitoring
        """
        wrapper = f'''
# SuperDiagnostic Safety Wrapper
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Execution log
$LogFile = "$env:TEMP\\superdiagnostic_execution_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

function Log-Action {{
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp : $Message"
    Add-Content -Path $LogFile -Value $logEntry
    Write-Host $logEntry
}}

function Log-Error {{
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp : ERROR: $Message"
    Add-Content -Path $LogFile -Value $logEntry
    Write-Error $logEntry
}}

try {{
    Log-Action "═══════════════════════════════════════════"
    Log-Action "SuperDiagnostic Remediation Script Started"
    Log-Action "═══════════════════════════════════════════"
    Log-Action "Log file: $LogFile"
    Log-Action ""
    
    # Original script execution
{self._indent_script(script, 4)}
    
    Log-Action ""
    Log-Action "═══════════════════════════════════════════"
    Log-Action "Script completed successfully"
    Log-Action "═══════════════════════════════════════════"
    exit 0
}}
catch {{
    Log-Error "Script execution failed"
    Log-Error "Error: $_"
    Log-Error "Line: $($_.InvocationInfo.ScriptLineNumber)"
    Log-Error "Command: $($_.InvocationInfo.Line)"
    exit 1
}}
finally {{
    Log-Action "Execution log saved to: $LogFile"
}}
'''
        return wrapper
    
    def _indent_script(self, script: str, spaces: int) -> str:
        """
        Indent script lines for proper nesting.
        
        Args:
            script: Script to indent
            spaces: Number of spaces to indent
            
        Returns:
            Indented script
        """
        indent = ' ' * spaces
        lines = script.split('\n')
        indented_lines = [indent + line if line.strip() else line for line in lines]
        return '\n'.join(indented_lines)
    
    @staticmethod
    def get_last_execution_log() -> Optional[str]:
        """
        Retrieve the last execution log file content.
        
        Returns:
            Log content or None if not found
        """
        try:
            temp_dir = os.environ.get('TEMP', '')
            if not temp_dir:
                return None
            
            # Find most recent log file
            log_pattern = "superdiagnostic_execution_*.log"
            log_files = list(Path(temp_dir).glob(log_pattern))
            
            if not log_files:
                return None
            
            # Get most recent
            latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
            
            with open(latest_log, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception:
            return None
