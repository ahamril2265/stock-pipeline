import random
from datetime import datetime, UTC, timedelta


# ==========================================================
# Recovery KPIs
# ==========================================================

def get_recovery_metrics():

    recovered = random.randint(120, 180)

    retries = random.randint(0, 8)

    dlq = random.randint(0, 2)

    success = round(
        recovered /
        (recovered + retries + dlq)
        * 100,
        2
    )

    return {

        "recovered_messages": recovered,

        "retry_queue": retries,

        "dead_letter_queue": dlq,

        "recovery_success": success

    }


# ==========================================================
# Bronze Layer
# ==========================================================

def bronze_status():

    return {

        "records": random.randint(
            45000,
            55000
        ),

        "latest_write":

            datetime.now(
                UTC
            ) - timedelta(
                seconds=random.randint(
                    1,
                    5
                )
            ),

        "checkpoint": True,

        "quarantined":

            random.randint(
                0,
                3
            ),

        "latency":

            round(
                random.uniform(
                    0.2,
                    1.4
                ),
                2
            )

    }


# ==========================================================
# Silver Layer
# ==========================================================

def silver_status():

    return {

        "processed":

            random.randint(
                30000,
                45000
            ),

        "duplicates":

            random.randint(
                0,
                8
            ),

        "rejected":

            random.randint(
                0,
                3
            ),

        "checkpoint": True,

        "latency":

            round(
                random.uniform(
                    0.4,
                    1.8
                ),
                2
            )

    }


# ==========================================================
# Gold Layer
# ==========================================================

def gold_status():

    return {

        "tables": 4,

        "rows":

            random.randint(
                800,
                1300
            ),

        "refresh":

            datetime.now(
                UTC
            ) - timedelta(
                seconds=random.randint(
                    1,
                    8
                )
            ),

        "failures":

            random.randint(
                0,
                1
            )

    }


# ==========================================================
# Pipeline Flow
# ==========================================================

def pipeline_flow():

    return [

        {

            "name": "Producer",

            "healthy": True

        },

        {

            "name": "Kafka",

            "healthy": True

        },

        {

            "name": "Bronze",

            "healthy": True

        },

        {

            "name": "Silver",

            "healthy": True

        },

        {

            "name": "Gold",

            "healthy": True

        },

        {

            "name": "Dashboard",

            "healthy": True

        }

    ]


# ==========================================================
# Failure Events
# ==========================================================

def failure_events():

    now = datetime.now(UTC)

    return [

        {

            "time":

                now -

                timedelta(minutes=3),

            "component":

                "Spark",

            "event":

                "Executor Lost",

            "status":

                "Recovered"

        },

        {

            "time":

                now -

                timedelta(minutes=2),

            "component":

                "Kafka",

            "event":

                "Broker Timeout",

            "status":

                "Recovered"

        },

        {

            "time":

                now -

                timedelta(minutes=1),

            "component":

                "Bronze",

            "event":

                "Write Retry",

            "status":

                "Recovered"

        }

    ]


# ==========================================================
# Recovery Statistics
# ==========================================================

def recovery_statistics():

    return {

        "avg_recovery":

            round(

                random.uniform(
                    0.8,
                    2.2
                ),

                2

            ),

        "max_recovery":

            round(

                random.uniform(
                    3,
                    6
                ),

                2

            ),

        "total_recoveries":

            random.randint(
                180,
                350
            ),

        "successful_retries":

            random.randint(
                150,
                250
            ),

        "failed_retries":

            random.randint(
                0,
                4
            )

    }


# ==========================================================
# Alerts
# ==========================================================

def alerts():

    items = []

    if random.random() < 0.2:

        items.append(

            "⚠ Bronze write latency increased."

        )

    if random.random() < 0.15:

        items.append(

            "⚠ Spark executor restarted."

        )

    if random.random() < 0.10:

        items.append(

            "⚠ Kafka broker recovered."

        )

    return items