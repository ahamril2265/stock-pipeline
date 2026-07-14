import json
import os
from datetime import datetime
from typing import Dict, Any, List

LOG_FILE = "incident_logs.json"

def get_logs() -> List[Dict[str, Any]]:
    """Retrieve all incident logs."""
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def log_incident(service: str, severity: str, failure_type: str, 
                 recovered: bool = False, recovery_time: float = 0.0, 
                 action_taken: str = "") -> None:
    """Log a new incident or update an existing one."""
    logs = get_logs()
    
    incident = {
        "timestamp": datetime.now().isoformat(),
        "service": service,
        "severity": severity,
        "failure_type": failure_type,
        "recovered": recovered,
        "recovery_time": round(recovery_time, 2),
        "action_taken": action_taken
    }
    
    logs.append(incident)
    
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)

def update_incident_recovery(service: str, recovery_time: float, action_taken: str) -> None:
    """Update the most recent unrecovered incident for a service as recovered."""
    logs = get_logs()
    
    for log in reversed(logs):
        if log["service"] == service and not log["recovered"]:
            log["recovered"] = True
            log["recovery_time"] = round(recovery_time, 2)
            log["action_taken"] = action_taken
            break
            
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)
