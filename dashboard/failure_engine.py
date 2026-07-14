import docker
from typing import Dict, Any, Optional

def _get_client() -> Optional[docker.DockerClient]:
    try:
        return docker.from_env()
    except Exception as e:
        print(f"Failed to initialize Docker client: {e}")
        return None

def get_container(name: str):
    client = _get_client()
    if not client:
        return None
    try:
        return client.containers.get(name)
    except docker.errors.NotFound:
        print(f"Container {name} not found.")
        return None
    except Exception as e:
        print(f"Error retrieving container {name}: {e}")
        return None

def stop_service(service_name: str) -> bool:
    """Gracefully stop a container."""
    container = get_container(service_name)
    if container:
        try:
            container.stop()
            return True
        except Exception as e:
            print(f"Error stopping {service_name}: {e}")
    return False

def kill_service(service_name: str) -> bool:
    """Forcefully kill a container."""
    container = get_container(service_name)
    if container:
        try:
            container.kill()
            return True
        except Exception as e:
            print(f"Error killing {service_name}: {e}")
    return False

def restart_service(service_name: str) -> bool:
    """Restart a container."""
    container = get_container(service_name)
    if container:
        try:
            container.restart()
            return True
        except Exception as e:
            print(f"Error restarting {service_name}: {e}")
    return False

def start_service(service_name: str) -> bool:
    """Start a stopped container."""
    container = get_container(service_name)
    if container:
        try:
            container.start()
            return True
        except Exception as e:
            print(f"Error starting {service_name}: {e}")
    return False

def pause_service(service_name: str) -> bool:
    """Pause a container."""
    container = get_container(service_name)
    if container:
        try:
            container.pause()
            return True
        except Exception as e:
            print(f"Error pausing {service_name}: {e}")
    return False

def unpause_service(service_name: str) -> bool:
    """Unpause a container."""
    container = get_container(service_name)
    if container:
        try:
            container.unpause()
            return True
        except Exception as e:
            print(f"Error unpausing {service_name}: {e}")
    return False

def inspect_service(service_name: str) -> Optional[Dict[str, Any]]:
    """Inspect a container and return its attributes."""
    container = get_container(service_name)
    if container:
        try:
            return container.attrs
        except Exception:
            pass
    return None
