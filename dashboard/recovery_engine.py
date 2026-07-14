import json
import os
import time
import threading
from typing import Dict, Any

from health import all_services
from failure_engine import restart_service, start_service
from incident_logger import update_incident_recovery, log_incident, get_logs

RECOVERY_STATE_FILE = "recovery_state.json"
CONFIG_FILE = "system_config.json"

DEFAULT_CONFIG = {
    "retry_count": 3,
    "chaos_interval_min": 30,
    "chaos_interval_max": 90,
    "chaos_probability": 0.5,
    "max_simultaneous_failures": 2
}

def get_config() -> Dict[str, Any]:
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_CONFIG

def save_config(config: Dict[str, Any]) -> None:
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def load_recovery_state() -> Dict[str, Any]:
    if not os.path.exists(RECOVERY_STATE_FILE):
        return {}
    try:
        with open(RECOVERY_STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_recovery_state(state: Dict[str, Any]) -> None:
    with open(RECOVERY_STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

SERVICE_MAPPINGS = {
    "Kafka": "kafka",
    "Spark": "spark-worker",  # In health.py Spark maps to spark-master API but failure maps to containers
                              # Actually health.py checks Spark master.
    "Schema Registry": "schema-registry",
    "ClickHouse": "clickhouse",
    "PostgreSQL": "postgres",
    "MinIO": "minio",
    "Airflow": "airflow-webserver" # Or scheduler
}

def tick_recovery() -> None:
    """Run a recovery check cycle."""
    services = all_services()
    state = load_recovery_state()
    config = get_config()
    max_retries = config.get("retry_count", 3)
    
    current_time = time.time()
    
    for service_name, is_healthy in services.items():
        container_name = SERVICE_MAPPINGS.get(service_name, service_name.lower())
        
        if not is_healthy:
            if service_name not in state:
                # First time detected as down
                state[service_name] = {
                    "status": "Waiting",
                    "retries": 0,
                    "first_failure_time": current_time,
                    "last_attempt_time": 0
                }
            
            svc_state = state[service_name]
            
            # Unlogged failure detection (if not logged by chaos or manual)
            logs = get_logs()
            unrecovered = [l for l in logs if l["service"] == container_name and not l["recovered"]]
            if not unrecovered:
                 log_incident(
                     service=container_name,
                     severity="High",
                     failure_type="Unexpected Outage"
                 )
            
            if svc_state["retries"] < max_retries:
                # Attempt recovery
                if current_time - svc_state["last_attempt_time"] > 10: # Wait 10s between retries
                    svc_state["status"] = "Restarting"
                    
                    def async_restart(c_name):
                        success = restart_service(c_name)
                        if not success:
                            start_service(c_name)
                            
                    threading.Thread(target=async_restart, args=(container_name,)).start()
                    
                    svc_state["retries"] += 1
                    svc_state["last_attempt_time"] = current_time
            else:
                svc_state["status"] = "Failed"
                
        else:
            # Healthy
            if service_name in state:
                # Was down, now recovered
                svc_state = state[service_name]
                downtime = current_time - svc_state["first_failure_time"]
                
                update_incident_recovery(
                    service=container_name, 
                    recovery_time=downtime, 
                    action_taken=f"Auto-recovered after {svc_state['retries']} retries"
                )
                
                del state[service_name]
                
    save_recovery_state(state)

def recover_manual(service: str) -> bool:
    """Manually initiate a recovery for a service."""
    state = load_recovery_state()
    # Reset state to force retry immediately
    for k, v in SERVICE_MAPPINGS.items():
        if v == service:
            if k in state:
               del state[k]
               save_recovery_state(state)
            break
            
    def async_manual_restart(c_name):
        success = restart_service(c_name)
        if not success:
            start_service(c_name)
            
    threading.Thread(target=async_manual_restart, args=(service,)).start()
    return True

def get_recovery_status() -> Dict[str, Any]:
    return load_recovery_state()
