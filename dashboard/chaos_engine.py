import json
import os
import random
import time
from datetime import datetime
from typing import List, Dict, Any

from failure_engine import stop_service, kill_service
from incident_logger import log_incident

CHAOS_STATE_FILE = "chaos_state.json"

TARGET_SERVICES = [
    "kafka",
    "schema-registry",
    "spark-master",
    "spark-worker",
    "clickhouse",
    "minio",
    "postgres",
    "airflow-scheduler",
    "airflow-webserver",
    "producer"
]

def load_chaos_state() -> Dict[str, Any]:
    if not os.path.exists(CHAOS_STATE_FILE):
        return {"enabled": False, "mode": "Disabled", "last_event_time": 0}
    try:
        with open(CHAOS_STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"enabled": False, "mode": "Disabled", "last_event_time": 0}

def save_chaos_state(state: Dict[str, Any]) -> None:
    with open(CHAOS_STATE_FILE, "w") as f:
        json.dump(state, f)

def enable_chaos(mode: str) -> None:
    """Enable chaos testing."""
    state = load_chaos_state()
    state["enabled"] = mode != "Disabled"
    state["mode"] = mode
    save_chaos_state(state)

def tick_chaos() -> None:
    """Called periodically to inject failures if active and random mode is on."""
    state = load_chaos_state()
    
    if not state.get("enabled") or state.get("mode") != "Random":
        return
        
    current_time = time.time()
    last_time = state.get("last_event_time", 0)
    interval = state.get("interval", random.randint(30, 90))
    
    if current_time - last_time >= interval:
        # Time for chaos
        target = random.choice(TARGET_SERVICES)
        action = random.choice(["stop", "kill"])
        
        success = False
        if action == "stop":
            success = stop_service(target)
        else:
            success = kill_service(target)
            
        if success:
            log_incident(
                service=target,
                severity="High",
                failure_type=f"Chaos {action.capitalize()}",
                action_taken="None (Chaos Injection)"
            )
        
        state["last_event_time"] = current_time
        state["interval"] = random.randint(30, 90)
        save_chaos_state(state)

def inject_manual_failure(service: str) -> bool:
    """Manually inject a failure into a service."""
    success = stop_service(service)
    if success:
         log_incident(
            service=service,
            severity="Critical",
            failure_type="Manual Stop",
            action_taken="None (Manual Injection)"
         )
    return success
