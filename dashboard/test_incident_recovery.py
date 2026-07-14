import time
import pytest
from failure_engine import stop_service, get_container
from recovery_engine import recover_manual, tick_recovery, get_recovery_status
from chaos_engine import inject_manual_failure
from health import all_services

# We assume Docker is running and containers (e.g. kafka) are available for testing.

TEST_TARGET = "kafka"

def test_inject_manual_failure():
    # Attempt to inject a failure manually
    success = inject_manual_failure(TEST_TARGET)
    
    # Check if container actually stopped
    container = get_container(TEST_TARGET)
    if container:
        container.reload()
        assert container.status in ('exited', 'dead', 'paused')
        
def test_tick_recovery():
    # Verify the recovery engine detects it
    tick_recovery()
    
    state = get_recovery_status()
    # It might use the internal mapping for uppercase names, so check all values
    statuses = [s["status"] for s in state.values()]
    assert "Restarting" in statuses or "Waiting" in statuses
    
def test_service_healthy_again():
    # Wait for the service to actually come back online
    time.sleep(10)
    
    # Manual check
    services = all_services()
    assert services.get("Kafka", False) is True
    
def test_recover_manual():
    # Stop it again
    stop_service("kafka")
    
    # Recover manually
    recover_manual("kafka")
    time.sleep(10)
    
    services = all_services()
    assert services.get("Kafka", False) is True
