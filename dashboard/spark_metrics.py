import requests


# ==========================================================
# Configuration
# ==========================================================

SPARK_MASTER = "http://spark-master:8080"


# ==========================================================
# Spark Master JSON API
# ==========================================================

def spark_json():

    try:

        response = requests.get(
            f"{SPARK_MASTER}/json",
            timeout=3
        )

        response.raise_for_status()

        return response.json()

    except Exception:

        return None


# ==========================================================
# Health
# ==========================================================

def spark_alive():

    return spark_json() is not None


# ==========================================================
# Cluster Summary
# ==========================================================

def cluster_summary():

    data = spark_json()

    if data is None:

        return None

    workers = data.get("workers", [])

    alive_workers = [

        w for w in workers

        if w.get("state") == "ALIVE"

    ]

    total_cores = sum(
        w.get("cores", 0)
        for w in workers
    )

    used_cores = sum(
        w.get("coresused", 0)
        for w in workers
    )

    total_memory = sum(
        w.get("memory", 0)
        for w in workers
    )

    used_memory = sum(
        w.get("memoryused", 0)
        for w in workers
    )

    return {

        "workers": len(workers),

        "alive_workers": len(alive_workers),

        "dead_workers":
            len(workers) - len(alive_workers),

        "applications":
            len(data.get("activeapps", [])),

        "completed_apps":
            len(data.get("completedapps", [])),

        "drivers":
            len(data.get("activedrivers", [])),

        "completed_drivers":
            len(data.get("completeddrivers", [])),

        "cores_total":
            total_cores,

        "cores_used":
            used_cores,

        "cores_free":
            total_cores - used_cores,

        "memory_total":
            total_memory,

        "memory_used":
            used_memory,

        "memory_free":
            total_memory - used_memory

    }


# ==========================================================
# Workers
# ==========================================================

def workers():

    data = spark_json()

    if data is None:

        return []

    output = []

    for worker in data.get("workers", []):

        cpu = 0

        if worker.get("cores", 0):

            cpu = round(
                worker["coresused"] /
                worker["cores"] * 100,
                1
            )

        memory = 0

        if worker.get("memory", 0):

            memory = round(
                worker["memoryused"] /
                worker["memory"] * 100,
                1
            )

        output.append({

            "Worker":
                worker["id"],

            "Host":
                worker["host"],

            "State":
                worker["state"],

            "Cores":
                worker["cores"],

            "Used Cores":
                worker["coresused"],

            "CPU %":
                cpu,

            "Memory MB":
                worker["memory"],

            "Used Memory MB":
                worker["memoryused"],

            "Memory %":
                memory

        })

    return output


# ==========================================================
# Applications
# ==========================================================

def applications():

    data = spark_json()

    if data is None:

        return []

    output = []

    for app in data.get("activeapps", []):

        output.append({

            "Application":
                app.get("name"),

            "ID":
                app.get("id"),

            "Cores":
                app.get("cores"),

            "Memory":
                app.get("memoryperslave"),

            "Start":
                app.get("starttime"),

            "Duration":
                app.get("duration")

        })

    return output


# ==========================================================
# Resource Usage
# ==========================================================

def resource_usage():

    summary = cluster_summary()

    if summary is None:

        return None

    cpu = 0

    memory = 0

    if summary["cores_total"]:

        cpu = round(

            summary["cores_used"]

            /

            summary["cores_total"]

            * 100,

            1

        )

    if summary["memory_total"]:

        memory = round(

            summary["memory_used"]

            /

            summary["memory_total"]

            * 100,

            1

        )

    return {

        "cpu": cpu,

        "memory": memory

    }


# ==========================================================
# Cluster Metrics
# ==========================================================

def cluster_metrics():

    summary = cluster_summary()

    usage = resource_usage()

    if summary is None:

        return None

    return {

        **summary,

        "cpu_usage":
            usage["cpu"],

        "memory_usage":
            usage["memory"],

        "cluster_utilization":

            round(

                (

                    usage["cpu"]

                    +

                    usage["memory"]

                ) / 2,

                1

            )

    }