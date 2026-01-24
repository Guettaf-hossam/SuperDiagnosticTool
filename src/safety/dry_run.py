"""Dry-run simulator for PowerShell scripts - preview changes without execution."""

import re
from typing import Dict, List, Set


class DryRunSimulator:
    """Simulate PowerShell script execution to preview changes."""
    
    @staticmethod
    def simulate(script: str) -> Dict:
        """
        Simulate what the script would do without executing.
        
        Args:
            script: PowerShell script content
            
        Returns:
            Dictionary with impact analysis
        """
        result = {
            'services_affected': [],
            'files_affected': [],
            'registry_affected': [],
            'processes_affected': [],
            'network_changes': [],
            'estimated_risk': 'LOW',
            'total_changes': 0,
            'change_summary': []
        }
        
        # Analyze services
        service_patterns = {
            r'Stop-Service\s+["\']?([^"\'\s]+)': 'STOP',
            r'Start-Service\s+["\']?([^"\'\s]+)': 'START',
            r'Restart-Service\s+["\']?([^"\'\s]+)': 'RESTART',
            r'Set-Service\s+["\']?([^"\'\s]+).*-StartupType\s+(\w+)': 'CONFIGURE',
            r'Disable-Service\s+["\']?([^"\'\s]+)': 'DISABLE',
        }
        
        for pattern, action in service_patterns.items():
            matches = re.findall(pattern, script, re.IGNORECASE)
            for match in matches:
                service_name = match if isinstance(match, str) else match[0]
                result['services_affected'].append({
                    'name': service_name,
                    'action': action
                })
                result['change_summary'].append(f"{action} service: {service_name}")
        
        # Analyze file operations
        file_patterns = {
            r'Remove-Item\s+["\']?([^"\']+)': 'DELETE',
            r'Delete\s+["\']?([^"\']+)': 'DELETE',
            r'New-Item\s+["\']?([^"\']+)': 'CREATE',
            r'Set-Content\s+["\']?([^"\']+)': 'MODIFY',
            r'Clear-Content\s+["\']?([^"\']+)': 'CLEAR',
        }
        
        for pattern, action in file_patterns.items():
            matches = re.findall(pattern, script, re.IGNORECASE)
            for match in matches:
                result['files_affected'].append({
                    'path': match,
                    'action': action
                })
                result['change_summary'].append(f"{action} file: {match}")
        
        # Analyze registry operations
        registry_patterns = {
            r'Set-ItemProperty.*Registry.*["\']?([^"\']+)': 'MODIFY',
            r'New-ItemProperty.*Registry.*["\']?([^"\']+)': 'CREATE',
            r'Remove-ItemProperty.*Registry.*["\']?([^"\']+)': 'DELETE',
            r'reg\s+add\s+([^\s]+)': 'ADD',
            r'reg\s+delete\s+([^\s]+)': 'DELETE',
        }
        
        for pattern, action in registry_patterns.items():
            matches = re.findall(pattern, script, re.IGNORECASE)
            for match in matches:
                result['registry_affected'].append({
                    'key': match,
                    'action': action
                })
                result['change_summary'].append(f"{action} registry: {match}")
        
        # Analyze process operations
        process_patterns = {
            r'Stop-Process\s+.*-Name\s+["\']?([^"\'\s]+)': 'STOP',
            r'Stop-Process\s+.*-Id\s+(\d+)': 'STOP',
            r'Start-Process\s+["\']?([^"\']+)': 'START',
        }
        
        for pattern, action in process_patterns.items():
            matches = re.findall(pattern, script, re.IGNORECASE)
            for match in matches:
                result['processes_affected'].append({
                    'name': match,
                    'action': action
                })
                result['change_summary'].append(f"{action} process: {match}")
        
        # Analyze network changes
        network_patterns = [
            r'netsh.*firewall',
            r'netsh.*advfirewall',
            r'Set-NetFirewallRule',
            r'New-NetFirewallRule',
            r'Clear-DnsClientCache',
            r'ipconfig\s+/flushdns',
        ]
        
        for pattern in network_patterns:
            matches = re.findall(pattern, script, re.IGNORECASE)
            if matches:
                result['network_changes'].extend(matches)
                result['change_summary'].append(f"Network change: {matches[0]}")
        
        # Calculate total changes
        result['total_changes'] = (
            len(result['services_affected']) +
            len(result['files_affected']) +
            len(result['registry_affected']) +
            len(result['processes_affected']) +
            len(result['network_changes'])
        )
        
        # Estimate risk level
        result['estimated_risk'] = DryRunSimulator._calculate_risk(result)
        
        return result
    
    @staticmethod
    def _calculate_risk(analysis: Dict) -> str:
        """
        Calculate risk level based on analysis.
        
        Args:
            analysis: Analysis results
            
        Returns:
            Risk level string
        """
        total = analysis['total_changes']
        
        # Weight different types of changes
        risk_score = 0
        risk_score += len(analysis['services_affected']) * 2
        risk_score += len(analysis['files_affected']) * 3
        risk_score += len(analysis['registry_affected']) * 4
        risk_score += len(analysis['processes_affected']) * 1
        risk_score += len(analysis['network_changes']) * 3
        
        # Check for high-risk operations
        for item in analysis['files_affected']:
            if item['action'] == 'DELETE':
                risk_score += 5
        
        for item in analysis['registry_affected']:
            if 'HKLM' in item['key']:
                risk_score += 5
        
        # Determine risk level
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
    
    @staticmethod
    def format_summary(analysis: Dict) -> str:
        """
        Format analysis results as human-readable summary.
        
        Args:
            analysis: Analysis results
            
        Returns:
            Formatted summary string
        """
        lines = []
        lines.append("═══ DRY-RUN SIMULATION RESULTS ═══\n")
        
        lines.append(f"Total Changes: {analysis['total_changes']}")
        lines.append(f"Risk Level: {analysis['estimated_risk']}\n")
        
        if analysis['services_affected']:
            lines.append(f"Services ({len(analysis['services_affected'])}):")
            for svc in analysis['services_affected'][:5]:  # Show first 5
                lines.append(f"  • {svc['action']}: {svc['name']}")
            if len(analysis['services_affected']) > 5:
                lines.append(f"  ... and {len(analysis['services_affected']) - 5} more")
            lines.append("")
        
        if analysis['files_affected']:
            lines.append(f"Files ({len(analysis['files_affected'])}):")
            for file in analysis['files_affected'][:5]:
                lines.append(f"  • {file['action']}: {file['path']}")
            if len(analysis['files_affected']) > 5:
                lines.append(f"  ... and {len(analysis['files_affected']) - 5} more")
            lines.append("")
        
        if analysis['registry_affected']:
            lines.append(f"Registry ({len(analysis['registry_affected'])}):")
            for reg in analysis['registry_affected'][:5]:
                lines.append(f"  • {reg['action']}: {reg['key']}")
            if len(analysis['registry_affected']) > 5:
                lines.append(f"  ... and {len(analysis['registry_affected']) - 5} more")
            lines.append("")
        
        if analysis['processes_affected']:
            lines.append(f"Processes ({len(analysis['processes_affected'])}):")
            for proc in analysis['processes_affected'][:5]:
                lines.append(f"  • {proc['action']}: {proc['name']}")
            lines.append("")
        
        if analysis['network_changes']:
            lines.append(f"Network Changes ({len(analysis['network_changes'])}):")
            for net in analysis['network_changes'][:3]:
                lines.append(f"  • {net}")
            lines.append("")
        
        return '\n'.join(lines)
