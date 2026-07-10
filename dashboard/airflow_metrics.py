import requests

# ==========================================================
# Configuration
# ==========================================================

AIRFLOW_URL = "http://airflow-webserver:8080"

AIRFLOW_USERNAME = "admin"

AIRFLOW_PASSWORD = "admin"

AUTH = (AIRFLOW_USERNAME, AIRFLOW_PASSWORD)


# ==========================================================
# Request Helper
# ==========================================================

def api(endpoint):

    try:

        response = requests.get(

            AIRFLOW_URL + endpoint,

            auth=AUTH,

            timeout=5

        )

        response.raise_for_status()

        return response.json()

    except Exception:

        return None


# ==========================================================
# Health
# ==========================================================

def airflow_alive():

    return api("/api/v1/health") is not None


# ==========================================================
# Health Details
# ==========================================================

def health():

    data = api("/api/v1/health")

    if data is None:

        return None

    return {

        "metadatabase":

            data["metadatabase"]["status"],

        "scheduler":

            data["scheduler"]["status"]

    }


# ==========================================================
# DAGs
# ==========================================================

def dags():

    data = api("/api/v1/dags")

    if data is None:

        return []

    items = []

    for dag in data.get("dags", []):

        items.append({

            "DAG ID":

                dag["dag_id"],

            "Paused":

                dag["is_paused"],

            "File":

                dag["fileloc"]

        })

    return items


# ==========================================================
# DAG Runs
# ==========================================================

def dag_runs(dag_id):

    data = api(

        f"/api/v1/dags/{dag_id}/dagRuns"

    )

    if data is None:

        return []

    runs = []

    for run in data.get("dag_runs", []):

        runs.append({

            "Run ID":

                run["dag_run_id"],

            "State":

                run["state"],

            "Execution":

                run["execution_date"],

            "Start":

                run["start_date"],

            "End":

                run["end_date"]

        })

    return runs


# ==========================================================
# Summary
# ==========================================================

def summary():

    dag_list = dags()

    active = len(

        [d for d in dag_list if not d["Paused"]]

    )

    paused = len(

        [d for d in dag_list if d["Paused"]]

    )

    return {

        "total": len(dag_list),

        "active": active,

        "paused": paused

    }