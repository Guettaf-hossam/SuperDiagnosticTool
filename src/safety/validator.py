"""Multi-level PowerShell script validation and critical-path interception."""

import re
import os
import json
import tempfile
import subprocess
from typing import Tuple, List, Dict


class CriticalPathInterceptor:
    """Zero-trust gate for Registry and System32 modifications.

    Scans a PowerShell script for any operation that touches the Windows
    Registry or system-critical filesystem paths. Detection halts the
    pipeline and forces explicit manual confirmation before execution
    can proceed.
    """

    CRITICAL_PATTERNS: List[Dict[str, str]] = [
        {"pattern": r"HKLM\\", "label": "HKEY_LOCAL_MACHINE registry access"},
        {"pattern": r"HKCU\\", "label": "HKEY_CURRENT_USER registry access"},
        {"pattern": r"reg\s+(add|delete)", "label": "Registry key modification via reg.exe"},
        {"pattern": r"Set-ItemProperty.*Registry", "label": "Registry property modification"},
        {"pattern": r"Remove-ItemProperty.*Registry", "label": "Registry property removal"},
        {"pattern": r"C:\\Windows\\System32", "label": "System32 directory access"},
        {"pattern": r"\$env:SystemRoot", "label": "SystemRoot environment variable reference"},
    ]

    @classmethod
    def intercept(cls, script: str) -> Tuple[bool, List[str]]:
        """Scan a script for critical-path operations.

        Args:
            script: The PowerShell script content to analyse.

        Returns:
            A tuple of (is_blocked, list_of_reasons). If is_blocked is
            True, execution must not proceed without explicit manual
            confirmation.
        """
        violations: List[str] = []

        for entry in cls.CRITICAL_PATTERNS:
            matches = re.findall(entry["pattern"], script, re.IGNORECASE)
            if matches:
                violations.append(
                    f"{entry['label']} (detected {len(matches)} occurrence(s))"
                )

        return (len(violations) > 0, violations)


class ScriptValidator:
    """Multi-level PowerShell script validation for safety."""

    BLACKLIST = [
        r'format\s+[a-z]:\s*$',
        r'del\s+/f\s+/s\s+/q\s+[a-z]:\\',
        r'rmdir\s+/s\s+/q\s+[a-z]:\\',
        r'reg\s+delete\s+HKLM\\SYSTEM',
        r'reg\s+delete\s+HKLM\\SOFTWARE\\Microsoft\\Windows',
        r'Remove-Item.*-Recurse.*C:\\Windows',
        r'Remove-Item.*-Recurse.*C:\\Program Files',
        r'Stop-Computer\s*$',
        r'Restart-Computer\s*$',
        r'Remove-Item.*\$env:SystemRoot',
        r'Format-Volume',
        r'Clear-Disk',
        r'Initialize-Disk.*-PartitionStyle',
    ]

    WHITELIST_COMMANDS = [
        'if', 'else', 'elseif', 'switch',
        'foreach', 'for', 'while', 'do',
        'function', 'param', 'return', 'exit', 'break', 'continue',
        'Try', 'Catch', 'Finally', 'throw',

        'Get-Service', 'Stop-Service', 'Start-Service',
        'Set-Service', 'Restart-Service',

        'Get-Process', 'Stop-Process',

        'Clear-DnsClientCache', 'ipconfig', 'netsh',

        'sfc', 'DISM', 'Dism', 'chkdsk',
        'Optimize-Volume', 'Clear-RecycleBin',

        'Write-Host', 'Write-Output', 'Write-Error',
        'Write-Warning', 'Write-Verbose',
        'Out-Null', 'Out-Host',

        'Get-Item', 'Get-ItemProperty',
        'Set-ItemProperty', 'New-ItemProperty', 'Remove-ItemProperty',
        'Test-Path', 'Get-Content', 'Set-Content', 'Clear-Content',
        'Get-ChildItem', 'Remove-Item', 'Join-Path',

        'Get-WmiObject', 'Get-CimInstance',
        'Get-Volume', 'Get-PhysicalDisk',

        'Start-Sleep', 'Wait-Process',
        'Where-Object', 'ForEach-Object',
        'Select-Object', 'Measure-Object',
    ]

    RISKY_PATTERNS = {
        r'Remove-Item(?!Property)': 4,
        r'Delete': 4,
        r'Disable-\w+': 3,
        r'Stop-Service': 2,
        r'Set-ItemProperty.*HKLM': 5,
        r'Set-ItemProperty.*HKCU': 3,
        r'reg\s+add': 4,
        r'reg\s+delete': 6,
        r'Remove-ItemProperty': 4,
        r'netsh.*firewall': 5,
        r'netsh.*advfirewall': 5,
        r'Set-ExecutionPolicy': 6,
        r'Start-Process': 3,
        r'-Force': 2,
        r'-Recurse': 3,
    }

    SUSPICIOUS_PATTERNS = [
        r'Invoke-WebRequest.*\|.*Invoke-Expression',
        r'IEX.*\(',
        r'powershell.*-enc',
        r'FromBase64String',
        r'DownloadString',
        r'DownloadFile',
        r'Start-BitsTransfer',
        r'System\.Net\.WebClient',
        r'Invoke-Expression',
        r'Invoke-Command',
        # PowerShell built-in aliases that bypass naive name matching.
        # 'ri' = Remove-Item, 'rd' = rmdir, 'kill' = Stop-Process.
        r'\bri\b\s+.*(C:\\|HKLM|HKCU)',
        r'\brd\b\s+/s',
        r'\bkill\b\s+-[Ff]',
        # String-concatenation obfuscation: "Rem"+"ove-Item", ('Re'+'move-Item')
        r'["\'][A-Za-z]+["\']\s*\+\s*["\'][a-z-]+["\']',
        # Backtick character insertion used to split keywords: R`emove-Item
        r'[A-Za-z]+`[A-Za-z]+',
    ]

    @classmethod
    def _extract_ast_commands(cls, script: str) -> List[str]:
        """Extract all command invocations using PowerShell AST."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False, encoding='utf-8') as f:
                f.write(script)
                temp_path = f.name
                
            ps_code = f"""
$ErrorActionPreference = 'SilentlyContinue'
$ast = [System.Management.Automation.Language.Parser]::ParseFile('{temp_path}', [ref]$null, [ref]$null)
$cmds = $ast.FindAll({{$args[0] -is [System.Management.Automation.Language.CommandAst]}}, $true) | ForEach-Object {{
    $n = $_.GetCommandName()
    if ($n) {{ $n }} else {{ "<DYNAMIC>" }}
}}
if ($cmds) {{
    @{{ cmds = @($cmds) }} | ConvertTo-Json -Compress
}} else {{
    '{{ "cmds": [] }}'
}}
"""
            result = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_code],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
            if result.returncode == 0 and result.stdout.strip():
                parsed = json.loads(result.stdout.strip())
                return parsed.get("cmds", [])
            return []
        except Exception:
            return []

    @classmethod
    def validate(cls, script: str) -> Tuple[bool, List[str], int]:
        """Validate PowerShell script with multi-level structural checks.

        Args:
            script: PowerShell script content.

        Returns:
            Tuple of (is_safe, warnings, risk_score).
        """
        warnings: List[str] = []
        risk_score = 0

        for pattern in cls.BLACKLIST:
            matches = re.findall(pattern, script, re.IGNORECASE | re.MULTILINE)
            if matches:
                return False, [f"BLOCKED: Dangerous pattern detected: {pattern}"], 100

        for pattern in cls.SUSPICIOUS_PATTERNS:
            matches = re.findall(pattern, script, re.IGNORECASE)
            if matches:
                warnings.append(f"SUSPICIOUS: Potentially malicious pattern: {pattern}")
                risk_score += 10

        ast_commands = cls._extract_ast_commands(script)
        if ast_commands:
            for cmd in ast_commands:
                if cmd == "<DYNAMIC>":
                    return False, ["BLOCKED: Dynamic/obfuscated invocation detected via AST"], 100
                if cmd not in cls.WHITELIST_COMMANDS:
                    warnings.append(f"Non-whitelisted command (AST detected): {cmd}")
                    risk_score += 3
        else:
            # Fallback to naive regex if AST parsing fails
            lines = script.split('\n')
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                cmd_match = re.match(r'^([A-Za-z][A-Za-z0-9-]*)', line)
                if cmd_match:
                    cmd = cmd_match.group(1)
                    if cmd not in cls.WHITELIST_COMMANDS and not cmd.startswith('$'):
                        warnings.append(f"Non-whitelisted command: {cmd} in line: {line[:50]}")
                        risk_score += 2

        for pattern, score in cls.RISKY_PATTERNS.items():
            matches = re.findall(pattern, script, re.IGNORECASE)
            if matches:
                count = len(matches)
                risk_score += score * count
                warnings.append(f"Risky pattern '{pattern}' found {count} time(s)")

        if len(script) > 10000:
            warnings.append("Script is very long (>10KB) - review carefully")
            risk_score += 5

        if script.count('\n') > 200:
            warnings.append("Script has many lines (>200) - review carefully")
            risk_score += 3

        is_safe = risk_score < 50
        return is_safe, warnings, risk_score

    @classmethod
    def get_risk_level(cls, risk_score: int) -> str:
        """Convert risk score to human-readable level.

        Args:
            risk_score: Numeric risk score.

        Returns:
            Risk level string.
        """
        if risk_score == 0:
            return "NONE"
        elif risk_score < 5:
            return "VERY LOW"
        elif risk_score < 10:
            return "LOW"
        elif risk_score < 20:
            return "MEDIUM"
        elif risk_score < 40:
            return "HIGH"
        return "CRITICAL"
