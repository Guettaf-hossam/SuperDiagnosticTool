"""System Restore Point Manager for safe system modifications."""

import subprocess
import datetime
import json
from typing import Tuple, Optional


class RestorePointManager:
    """Manages Windows System Restore Points for safe rollback."""
    
    @staticmethod
    def create_restore_point(description: str = "SuperDiagnostic Auto-Backup") -> Tuple[bool, str]:
        """
        Create a system restore point before any changes.
        
        Args:
            description: Description for the restore point
            
        Returns:
            (success, message): Tuple of success status and description/error message
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            full_desc = f"{description} - {timestamp}"
            
            ps_cmd = f'''
            try {{
                Checkpoint-Computer -Description "{full_desc}" -RestorePointType "MODIFY_SETTINGS" -ErrorAction Stop
                Write-Output "SUCCESS"
            }} catch {{
                Write-Output "FAILED: $_"
                exit 1
            }}
            '''
            
            result = subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                timeout=120,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0 and "SUCCESS" in result.stdout:
                return True, full_desc
            else:
                error_msg = result.stderr or result.stdout or "Unknown error"
                return False, error_msg.strip()
                
        except subprocess.TimeoutExpired:
            return False, "Timeout: Restore point creation took too long"
        except Exception as e:
            return False, f"Exception: {str(e)}"
    
    @staticmethod
    def verify_restore_point_exists(description: Optional[str] = None) -> bool:
        """
        Verify that a restore point was created successfully.
        
        Args:
            description: Optional description to search for
            
        Returns:
            True if restore point exists, False otherwise
        """
        try:
            if description:
                ps_cmd = f'''
                $rp = Get-ComputerRestorePoint | 
                    Where-Object {{$_.Description -like "*{description}*"}} | 
                    Select-Object -First 1
                if ($rp) {{ Write-Output "EXISTS" }} else {{ Write-Output "NOT_FOUND" }}
                '''
            else:
                ps_cmd = '''
                $rp = Get-ComputerRestorePoint | 
                    Where-Object {$_.Description -like "*SuperDiagnostic*"} | 
                    Select-Object -First 1
                if ($rp) { Write-Output "EXISTS" } else { Write-Output "NOT_FOUND" }
                '''
            
            result = subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            return "EXISTS" in result.stdout
            
        except Exception:
            return False
    
    @staticmethod
    def get_latest_restore_point() -> Optional[dict]:
        """
        Get information about the latest SuperDiagnostic restore point.
        
        Returns:
            Dictionary with restore point info or None
        """
        try:
            ps_cmd = '''
            $rp = Get-ComputerRestorePoint | 
                Where-Object {$_.Description -like "*SuperDiagnostic*"} | 
                Sort-Object CreationTime -Descending | 
                Select-Object -First 1 |
                Select-Object Description, CreationTime, SequenceNumber |
                ConvertTo-Json
            Write-Output $rp
            '''
            
            result = subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return json.loads(result.stdout)
            return None
            
        except Exception:
            return None
    
    @staticmethod
    def restore_to_point(sequence_number: int) -> Tuple[bool, str]:
        """
        Restore system to a specific restore point.
        
        Args:
            sequence_number: Sequence number of the restore point
            
        Returns:
            (success, message): Tuple of success status and message
        """
        try:
            ps_cmd = f'''
            try {{
                Restore-Computer -RestorePoint {sequence_number} -Confirm:$false -ErrorAction Stop
                Write-Output "RESTORE_INITIATED"
            }} catch {{
                Write-Output "FAILED: $_"
                exit 1
            }}
            '''
            
            result = subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                timeout=60,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0 and "RESTORE_INITIATED" in result.stdout:
                return True, "System restore initiated. Computer will restart."
            else:
                error_msg = result.stderr or result.stdout or "Unknown error"
                return False, error_msg.strip()
                
        except Exception as e:
            return False, f"Exception: {str(e)}"
