"""Enhanced monitoring system for systems without virtualization support."""

import json
import hashlib
import subprocess
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class EnhancedMonitoring:
    """
    Enhanced monitoring for safe script execution on systems without VM support.
    
    Provides:
    - Pre/post execution snapshots
    - Change detection
    - Selective rollback capabilities
    """
    
    def __init__(self):
        self.pre_snapshot = None
        self.post_snapshot = None
        self.changes_detected = []
        
    def take_snapshot(self) -> Dict:
        """
        Take comprehensive snapshot of system state.
        
        Returns:
            Dictionary containing system state
        """
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'services': self._get_services_state(),
            'startup_items': self._get_startup_items(),
            'critical_registry': self._get_critical_registry(),
            'system_info': self._get_system_info()
        }
        return snapshot
    
    def _get_services_state(self) -> Dict[str, str]:
        """Get state of all Windows services."""
        try:
            ps_cmd = '''
            Get-Service | Select-Object Name, Status, StartType | ConvertTo-Json
            '''
            
            result = subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0 and result.stdout:
                services = json.loads(result.stdout)
                if isinstance(services, dict):
                    services = [services]
                return {svc['Name']: {'Status': svc['Status'], 'StartType': svc['StartType']} 
                        for svc in services if svc}
            return {}
            
        except Exception:
            return {}
    
    def _get_startup_items(self) -> List[str]:
        """Get list of startup applications."""
        try:
            ps_cmd = '''
            Get-CimInstance Win32_StartupCommand | 
            Select-Object Name, Command | 
            ConvertTo-Json
            '''
            
            result = subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0 and result.stdout:
                items = json.loads(result.stdout)
                if isinstance(items, dict):
                    items = [items]
                return [f"{item['Name']}: {item['Command']}" for item in items if item]
            return []
            
        except Exception:
            return []
    
    def _get_critical_registry(self) -> Dict[str, str]:
        """Get critical registry keys that might be modified."""
        critical_keys = [
            r'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
            r'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
        ]
        
        registry_state = {}
        
        for key in critical_keys:
            try:
                ps_cmd = f'''
                if (Test-Path "{key}") {{
                    Get-ItemProperty "{key}" | ConvertTo-Json
                }}
                '''
                
                result = subprocess.run(
                    ["powershell", "-Command", ps_cmd],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    registry_state[key] = result.stdout.strip()
                    
            except Exception:
                continue
        
        return registry_state
    
    def _get_system_info(self) -> Dict:
        """Get basic system information."""
        try:
            ps_cmd = '''
            @{
                Uptime = (Get-Date) - (gcim Win32_OperatingSystem).LastBootUpTime
                TotalMemory = (gcim Win32_ComputerSystem).TotalPhysicalMemory
                FreeMemory = (gcim Win32_OperatingSystem).FreePhysicalMemory
            } | ConvertTo-Json
            '''
            
            result = subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0 and result.stdout:
                return json.loads(result.stdout)
            return {}
            
        except Exception:
            return {}
    
    def detect_changes(self, pre_snapshot: Dict, post_snapshot: Dict) -> List[Dict]:
        """
        Detect changes between two snapshots.
        
        Args:
            pre_snapshot: Snapshot before execution
            post_snapshot: Snapshot after execution
            
        Returns:
            List of detected changes
        """
        changes = []
        
        # Detect service changes
        pre_services = pre_snapshot.get('services', {})
        post_services = post_snapshot.get('services', {})
        
        for service_name, pre_state in pre_services.items():
            post_state = post_services.get(service_name)
            if post_state and post_state != pre_state:
                changes.append({
                    'type': 'service',
                    'name': service_name,
                    'before': pre_state,
                    'after': post_state
                })
        
        # Detect new services
        for service_name in post_services:
            if service_name not in pre_services:
                changes.append({
                    'type': 'service',
                    'name': service_name,
                    'before': None,
                    'after': post_services[service_name]
                })
        
        # Detect startup item changes
        pre_startup = set(pre_snapshot.get('startup_items', []))
        post_startup = set(post_snapshot.get('startup_items', []))
        
        new_items = post_startup - pre_startup
        removed_items = pre_startup - post_startup
        
        for item in new_items:
            changes.append({
                'type': 'startup_item',
                'action': 'added',
                'item': item
            })
        
        for item in removed_items:
            changes.append({
                'type': 'startup_item',
                'action': 'removed',
                'item': item
            })
        
        # Detect registry changes
        pre_registry = pre_snapshot.get('critical_registry', {})
        post_registry = post_snapshot.get('critical_registry', {})
        
        for key in set(list(pre_registry.keys()) + list(post_registry.keys())):
            pre_val = pre_registry.get(key, '')
            post_val = post_registry.get(key, '')
            if pre_val != post_val:
                changes.append({
                    'type': 'registry',
                    'key': key,
                    'before': pre_val[:100] if pre_val else None,
                    'after': post_val[:100] if post_val else None
                })
        
        return changes
    
    def generate_rollback_script(self, changes: List[Dict]) -> str:
        """
        Generate PowerShell script to rollback detected changes.
        
        Args:
            changes: List of changes to rollback
            
        Returns:
            PowerShell script for rollback
        """
        script_lines = [
            "# Auto-generated rollback script",
            "# Generated by SuperDiagnosticTool Enhanced Monitoring",
            f"# Timestamp: {datetime.now().isoformat()}",
            "",
            "$ErrorActionPreference = 'Continue'",
            ""
        ]
        
        for change in changes:
            if change['type'] == 'service':
                service_name = change['name']
                before_state = change.get('before', {})
                
                if before_state:
                    status = before_state.get('Status', 'Running')
                    start_type = before_state.get('StartType', 'Automatic')
                    
                    script_lines.append(f"# Restore service: {service_name}")
                    script_lines.append(f"Set-Service -Name '{service_name}' -StartupType {start_type} -ErrorAction SilentlyContinue")
                    
                    if status == 'Running':
                        script_lines.append(f"Start-Service -Name '{service_name}' -ErrorAction SilentlyContinue")
                    else:
                        script_lines.append(f"Stop-Service -Name '{service_name}' -ErrorAction SilentlyContinue")
                    
                    script_lines.append("")
        
        return '\n'.join(script_lines)
    
    def format_changes_report(self, changes: List[Dict]) -> str:
        """
        Format changes into human-readable report.
        
        Args:
            changes: List of detected changes
            
        Returns:
            Formatted report string
        """
        if not changes:
            return "No changes detected"
        
        lines = [f"Detected {len(changes)} change(s):\n"]
        
        for i, change in enumerate(changes, 1):
            if change['type'] == 'service':
                lines.append(f"{i}. Service: {change['name']}")
                if change.get('before'):
                    lines.append(f"   Before: {change['before']}")
                lines.append(f"   After:  {change['after']}")
                
            elif change['type'] == 'startup_item':
                lines.append(f"{i}. Startup Item {change['action']}: {change['item']}")
                
            elif change['type'] == 'registry':
                lines.append(f"{i}. Registry: {change['key']}")
                lines.append(f"   Modified")
            
            lines.append("")
        
        return '\n'.join(lines)
