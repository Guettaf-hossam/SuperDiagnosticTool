"""Multi-level PowerShell script validation system."""

import re
from typing import Tuple, List, Dict


class ScriptValidator:
    """Multi-level PowerShell script validation for safety."""
    
    # Level 1: Absolute blacklist (never allow these patterns)
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
    
    # Level 2: Whitelist (only these commands are considered safe)
    WHITELIST_COMMANDS = [
        'Get-Service',
        'Stop-Service',
        'Start-Service',
        'Set-Service',
        'Restart-Service',
        'Get-Process',
        'Stop-Process',
        'Clear-DnsClientCache',
        'ipconfig',
        'netsh',
        'sfc',
        'DISM',
        'chkdsk',
        'Write-Host',
        'Write-Output',
        'Write-Error',
        'Get-Item',
        'Get-ItemProperty',
        'Set-ItemProperty',
        'New-ItemProperty',
        'Remove-ItemProperty',
        'Test-Path',
        'Get-Content',
        'Set-Content',
        'Clear-Content',
        'Get-ChildItem',
        'Get-WmiObject',
        'Get-CimInstance',
        'Invoke-Expression',
        'Start-Sleep',
        'Wait-Process',
    ]
    
    # Level 3: Risk scoring patterns
    RISKY_PATTERNS = {
        r'Remove-Item(?!Property)': 4,  # File deletion
        r'Delete': 4,
        r'Disable-\w+': 3,  # Disabling services/features
        r'Stop-Service': 2,
        r'Set-ItemProperty.*HKLM': 5,  # Registry modification
        r'Set-ItemProperty.*HKCU': 3,
        r'reg\s+add': 4,
        r'reg\s+delete': 6,
        r'Remove-ItemProperty': 4,
        r'netsh.*firewall': 5,
        r'netsh.*advfirewall': 5,
        r'Set-ExecutionPolicy': 6,
        r'Invoke-Expression': 5,  # Code execution
        r'Invoke-Command': 5,
        r'Start-Process': 3,
        r'-Force': 2,  # Force flag
        r'-Recurse': 3,  # Recursive operations
    }
    
    # Suspicious patterns that should trigger warnings
    SUSPICIOUS_PATTERNS = [
        r'Invoke-WebRequest.*\|.*Invoke-Expression',  # Download and execute
        r'IEX.*\(',  # Invoke-Expression shorthand
        r'powershell.*-enc',  # Encoded commands
        r'FromBase64String',  # Base64 decoding
        r'DownloadString',  # Web downloads
        r'DownloadFile',
        r'Start-BitsTransfer',
        r'System\.Net\.WebClient',
    ]
    
    @classmethod
    def validate(cls, script: str) -> Tuple[bool, List[str], int]:
        """
        Validate PowerShell script with multi-level checks.
        
        Args:
            script: PowerShell script content
            
        Returns:
            (is_safe, warnings, risk_score): Validation results
        """
        warnings = []
        risk_score = 0
        
        # Level 1: Check blacklist (absolute blocking)
        for pattern in cls.BLACKLIST:
            matches = re.findall(pattern, script, re.IGNORECASE | re.MULTILINE)
            if matches:
                return False, [f"BLOCKED: Dangerous pattern detected: {pattern}"], 100
        
        # Check suspicious patterns
        for pattern in cls.SUSPICIOUS_PATTERNS:
            matches = re.findall(pattern, script, re.IGNORECASE)
            if matches:
                warnings.append(f"SUSPICIOUS: Potentially malicious pattern: {pattern}")
                risk_score += 10
        
        # Level 2: Check if commands are whitelisted
        lines = script.split('\n')
        non_whitelisted_count = 0
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Extract command (first word)
            cmd_match = re.match(r'^([A-Za-z][A-Za-z0-9-]*)', line)
            if cmd_match:
                cmd = cmd_match.group(1)
                if cmd not in cls.WHITELIST_COMMANDS and not cmd.startswith('$'):
                    non_whitelisted_count += 1
                    warnings.append(f"Non-whitelisted command: {cmd} in line: {line[:50]}")
                    risk_score += 2
        
        # Level 3: Calculate risk score from patterns
        for pattern, score in cls.RISKY_PATTERNS.items():
            matches = re.findall(pattern, script, re.IGNORECASE)
            if matches:
                count = len(matches)
                risk_score += score * count
                warnings.append(f"Risky pattern '{pattern}' found {count} time(s)")
        
        # Additional checks
        if len(script) > 10000:
            warnings.append("Script is very long (>10KB) - review carefully")
            risk_score += 5
        
        if script.count('\n') > 200:
            warnings.append("Script has many lines (>200) - review carefully")
            risk_score += 3
        
        # Determine overall safety
        is_safe = risk_score < 15
        
        return is_safe, warnings, risk_score
    
    @classmethod
    def get_risk_level(cls, risk_score: int) -> str:
        """
        Convert risk score to human-readable level.
        
        Args:
            risk_score: Numeric risk score
            
        Returns:
            Risk level string
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
        else:
            return "CRITICAL"
