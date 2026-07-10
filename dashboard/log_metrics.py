import subprocess
from datetime import datetime


# ==========================================================
# Containers
# ==========================================================

CONTAINERS = {

    "Kafka": "kafka",

    "Spark Master": "spark-master",

    "Spark Worker": "spark-worker",

    "Airflow Scheduler": "airflow-scheduler",

    "Airflow Webserver": "airflow-webserver",

    "ClickHouse": "clickhouse",

    "MinIO": "minio"

}


# ==========================================================
# Read Logs
# ==========================================================

def container_logs(container, lines=50):

    try:

        output = subprocess.check_output(

            [

                "docker",

                "logs",

                "--tail",

                str(lines),

                container

            ],

            stderr=subprocess.STDOUT,

            text=True

        )

        return output.splitlines()

    except Exception as e:

        return [

            f"Unable to read logs ({e})"

        ]


# ==========================================================
# Parse
# ==========================================================

def parse_logs(lines):

    parsed = []

    for line in reversed(lines):

        level = "INFO"

        if "ERROR" in line.upper():

            level = "ERROR"

        elif "WARN" in line.upper():

            level = "WARNING"

        elif "SUCCESS" in line.upper():

            level = "SUCCESS"

        parsed.append({

            "Time":

                datetime.now().strftime(

                    "%H:%M:%S"

                ),

            "Level":

                level,

            "Message":

                line

        })

    return parsed


# ==========================================================
# Container List
# ==========================================================

def containers():

    return list(

        CONTAINERS.keys()

    )


# ==========================================================
# Get Logs
# ==========================================================

def logs(service):

    container = CONTAINERS.get(service)

    if container is None:

        return []

    return parse_logs(

        container_logs(container)

    )