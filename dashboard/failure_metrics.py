from datetime import datetime, timedelta
from typing import Dict, Any

from incident_logger import get_logs

def calculate_metrics() -> Dict[str, Any]:
    logs = get_logs()
    
    total_failures = len(logs)
    recovered_incidents = [l for l in logs if l.get("recovered", False)]
    total_recoveries = len(recovered_incidents)
    
    recovery_percentage = 0.0
    if total_failures > 0:
        recovery_percentage = (total_recoveries / total_failures) * 100
        
    mean_recovery_time = 0.0
    longest_downtime = 0.0
    if total_recoveries > 0:
        recovery_times = [l.get("recovery_time", 0.0) for l in recovered_incidents]
        mean_recovery_time = sum(recovery_times) / total_recoveries
        longest_downtime = max(recovery_times)
        
    # Failures today
    today = datetime.now().date()
    failures_today = 0
    
    # Failures per service
    failures_by_service = {}
    
    for log in logs:
        try:
            log_date = datetime.fromisoformat(log.get("timestamp")).date()
            if log_date == today:
                failures_today += 1
        except Exception:
            pass
            
        svc = log.get("service", "Unknown")
        failures_by_service[svc] = failures_by_service.get(svc, 0) + 1
        
    return {
        "total_failures": total_failures,
        "total_recoveries": total_recoveries,
        "recovery_percentage": round(recovery_percentage, 1),
        "mean_recovery_time": round(mean_recovery_time, 2),
        "failures_today": failures_today,
        "failures_by_service": failures_by_service,
        "longest_downtime": round(longest_downtime, 2)
    }
