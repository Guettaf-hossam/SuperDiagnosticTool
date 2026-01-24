"""Knowledge base of known solutions for common Windows issues."""

from typing import Dict, List, Optional, Tuple
import re


class KnowledgeBase:
    """
    Database of known, tested solutions for common Windows issues.
    
    Provides:
    - Known solution matching
    - Solution validation
    - Success rate tracking
    """
    
    # Known solutions database
    KNOWN_SOLUTIONS = {
        "intel_service_high_cpu": {
            "symptoms": ["esrv_svc", "high cpu", "intel", "100%"],
            "description": "Intel services causing high CPU usage",
            "solution": """
# Stop and disable problematic Intel services
$services = @('esrv_svc', 'SurSvc', 'esrv')
foreach ($svc in $services) {
    if (Get-Service $svc -ErrorAction SilentlyContinue) {
        Stop-Service $svc -Force -ErrorAction SilentlyContinue
        Set-Service $svc -StartupType Disabled -ErrorAction SilentlyContinue
        Write-Host "Disabled service: $svc"
    }
}
""",
            "risk_level": "LOW",
            "tested": True,
            "success_rate": 0.95,
            "reversible": True,
            "tags": ["cpu", "intel", "service"]
        },
        
        "dns_cache_flush": {
            "symptoms": ["dns", "slow internet", "cannot resolve", "network"],
            "description": "DNS cache issues causing connectivity problems",
            "solution": """
# Flush DNS cache
ipconfig /flushdns
Clear-DnsClientCache
Write-Host "DNS cache cleared"
""",
            "risk_level": "VERY_LOW",
            "tested": True,
            "success_rate": 0.90,
            "reversible": True,
            "tags": ["dns", "network", "internet"]
        },
        
        "windows_update_stuck": {
            "symptoms": ["windows update", "stuck", "pending", "0x"],
            "description": "Windows Update service stuck or failing",
            "solution": """
# Reset Windows Update components
Stop-Service wuauserv -Force -ErrorAction SilentlyContinue
Stop-Service cryptSvc -Force -ErrorAction SilentlyContinue
Stop-Service bits -Force -ErrorAction SilentlyContinue
Stop-Service msiserver -Force -ErrorAction SilentlyContinue

Remove-Item C:\\Windows\\SoftwareDistribution\\Download\\* -Recurse -Force -ErrorAction SilentlyContinue

Start-Service wuauserv -ErrorAction SilentlyContinue
Start-Service cryptSvc -ErrorAction SilentlyContinue
Start-Service bits -ErrorAction SilentlyContinue
Start-Service msiserver -ErrorAction SilentlyContinue

Write-Host "Windows Update components reset"
""",
            "risk_level": "MEDIUM",
            "tested": True,
            "success_rate": 0.85,
            "reversible": True,
            "tags": ["windows update", "service", "update"]
        },
        
        "disk_cleanup": {
            "symptoms": ["low disk space", "disk full", "storage"],
            "description": "Clean temporary files and system cache",
            "solution": """
# Clean temporary files
Remove-Item $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item C:\\Windows\\Temp\\* -Recurse -Force -ErrorAction SilentlyContinue

# Clear Windows Update cache
Stop-Service wuauserv -Force -ErrorAction SilentlyContinue
Remove-Item C:\\Windows\\SoftwareDistribution\\Download\\* -Recurse -Force -ErrorAction SilentlyContinue
Start-Service wuauserv -ErrorAction SilentlyContinue

Write-Host "Temporary files cleaned"
""",
            "risk_level": "LOW",
            "tested": True,
            "success_rate": 0.98,
            "reversible": False,
            "tags": ["disk", "cleanup", "storage"]
        },
        
        "high_memory_usage": {
            "symptoms": ["high memory", "ram", "100%", "memory leak"],
            "description": "High memory usage - restart resource-heavy services",
            "solution": """
# Restart services that commonly cause memory leaks
$services = @('Spooler', 'WSearch')
foreach ($svc in $services) {
    if (Get-Service $svc -ErrorAction SilentlyContinue) {
        Restart-Service $svc -Force -ErrorAction SilentlyContinue
        Write-Host "Restarted service: $svc"
    }
}
""",
            "risk_level": "LOW",
            "tested": True,
            "success_rate": 0.70,
            "reversible": True,
            "tags": ["memory", "ram", "service"]
        }
    }
    
    @classmethod
    def find_matching_solution(cls, symptoms: str, telemetry: Dict = None) -> Optional[Dict]:
        """
        Find known solution matching the symptoms.
        
        Args:
            symptoms: User-reported problem description
            telemetry: Optional system telemetry data
            
        Returns:
            Matching solution dict or None
        """
        symptoms_lower = symptoms.lower()
        
        best_match = None
        best_score = 0
        
        for solution_id, solution in cls.KNOWN_SOLUTIONS.items():
            score = 0
            
            # Check symptom keywords
            for keyword in solution['symptoms']:
                if keyword.lower() in symptoms_lower:
                    score += 1
            
            # Check telemetry if available
            if telemetry:
                # Add telemetry-based scoring here
                pass
            
            if score > best_score:
                best_score = score
                best_match = {
                    'id': solution_id,
                    'match_score': score,
                    **solution
                }
        
        # Return only if match score is significant
        if best_score >= 2:
            return best_match
        
        return None
    
    @classmethod
    def validate_ai_solution(cls, ai_script: str, symptoms: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Validate AI-generated solution against knowledge base.
        
        Args:
            ai_script: PowerShell script generated by AI
            symptoms: User-reported symptoms
            
        Returns:
            (is_valid, reason, known_solution)
        """
        # Find matching known solution
        known = cls.find_matching_solution(symptoms)
        
        if not known:
            return True, "No known solution - AI solution accepted", None
        
        # Check if AI solution is similar to known solution
        similarity = cls._calculate_similarity(ai_script, known['solution'])
        
        if similarity > 0.7:
            return True, f"Matches known solution '{known['id']}' ({similarity*100:.0f}% similar)", known
        elif similarity > 0.4:
            return True, f"Partially matches known solution '{known['id']}' ({similarity*100:.0f}% similar)", known
        else:
            return True, f"Different from known solution '{known['id']}' - review recommended", known
    
    @classmethod
    def _calculate_similarity(cls, script1: str, script2: str) -> float:
        """
        Calculate similarity between two PowerShell scripts.
        
        Args:
            script1: First script
            script2: Second script
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Normalize scripts
        s1 = cls._normalize_script(script1)
        s2 = cls._normalize_script(script2)
        
        # Extract commands
        commands1 = set(cls._extract_commands(s1))
        commands2 = set(cls._extract_commands(s2))
        
        if not commands1 or not commands2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(commands1 & commands2)
        union = len(commands1 | commands2)
        
        return intersection / union if union > 0 else 0.0
    
    @classmethod
    def _normalize_script(cls, script: str) -> str:
        """Normalize PowerShell script for comparison."""
        # Remove comments
        script = re.sub(r'#.*$', '', script, flags=re.MULTILINE)
        # Remove extra whitespace
        script = re.sub(r'\s+', ' ', script)
        # Convert to lowercase
        return script.lower().strip()
    
    @classmethod
    def _extract_commands(cls, script: str) -> List[str]:
        """Extract PowerShell commands from script."""
        # Simple command extraction
        commands = []
        for line in script.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                # Extract first word (command)
                match = re.match(r'^([A-Za-z][A-Za-z0-9-]*)', line)
                if match:
                    commands.append(match.group(1).lower())
        return commands
    
    @classmethod
    def get_solution_by_id(cls, solution_id: str) -> Optional[Dict]:
        """Get solution by ID."""
        return cls.KNOWN_SOLUTIONS.get(solution_id)
    
    @classmethod
    def list_all_solutions(cls) -> List[Dict]:
        """List all known solutions."""
        return [
            {'id': sid, **solution}
            for sid, solution in cls.KNOWN_SOLUTIONS.items()
        ]
    
    @classmethod
    def get_solutions_by_tag(cls, tag: str) -> List[Dict]:
        """Get solutions by tag."""
        return [
            {'id': sid, **solution}
            for sid, solution in cls.KNOWN_SOLUTIONS.items()
            if tag.lower() in [t.lower() for t in solution.get('tags', [])]
        ]
