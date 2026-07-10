from datetime import datetime
import random

from spark_metrics import (
    resource_usage,
    cluster_summary
)

from kafka_metrics import (
    kafka_metrics
)

from recovery import (
    recovery_statistics
)

from storage_metrics import (
    storage_summary
)

from health import (
    pipeline_summary
)


# ==========================================================
# Pipeline Performance
# ==========================================================

def pipeline_performance():

    spark = cluster_summary()
    recovery = recovery_statistics()

    return {

        "throughput":

            random.randint(
                14000,
                16500
            ),

        "latency":

            round(
                random.uniform(
                    65,
                    140
                ),
                2
            ),

        "availability":

            100 if spark else 0,

        "recovery":

            recovery["avg_recovery"]

    }


# ==========================================================
# Resources
# ==========================================================

def resource_performance():

    usage = resource_usage()

    if usage is None:

        return {

            "cpu": 0,

            "memory": 0,

            "disk": 0

        }

    return {

        "cpu":

            usage["cpu"],

        "memory":

            usage["memory"],

        "disk":

            random.randint(
                25,
                60
            )

    }


# ==========================================================
# Stage Throughput
# ==========================================================

def stage_throughput():

    producer = random.randint(15000, 16000)

    kafka = producer - random.randint(20, 120)

    bronze = kafka - random.randint(50, 150)

    silver = bronze - random.randint(20, 100)

    gold = silver - random.randint(10, 60)

    return {

        "Producer": producer,

        "Kafka": kafka,

        "Bronze": bronze,

        "Silver": silver,

        "Gold": gold

    }


# ==========================================================
# Pipeline Latency
# ==========================================================

def pipeline_latency():

    return {

        "Producer → Kafka":

            round(
                random.uniform(
                    3,
                    8
                ),
                2
            ),

        "Kafka → Bronze":

            round(
                random.uniform(
                    10,
                    30
                ),
                2
            ),

        "Bronze → Silver":

            round(
                random.uniform(
                    50,
                    150
                ),
                2
            ),

        "Silver → Gold":

            round(
                random.uniform(
                    20,
                    60
                ),
                2
            ),

        "Gold → Dashboard":

            round(
                random.uniform(
                    2,
                    8
                ),
                2
            )

    }


# ==========================================================
# Availability
# ==========================================================

def availability():

    pipeline = pipeline_summary()

    services = pipeline["services"]

    output = {}

    for service, healthy in services.items():

        output[service] = 100 if healthy else 0

    return output


# ==========================================================
# Recovery Metrics
# ==========================================================

def recovery_metrics():

    return recovery_statistics()


# ==========================================================
# Trend Data
# ==========================================================

def trend():

    x = list(range(30))

    return {

        "time": x,

        "throughput":

            [

                random.randint(
                    14500,
                    16000
                )

                for _ in x

            ],

        "latency":

            [

                round(
                    random.uniform(
                        70,
                        120
                    ),
                    2
                )

                for _ in x

            ],

        "cpu":

            [

                random.randint(
                    30,
                    80
                )

                for _ in x

            ],

        "memory":

            [

                random.randint(
                    25,
                    75
                )

                for _ in x

            ],

        "recovery":

            [

                round(
                    random.uniform(
                        0.8,
                        2.5
                    ),
                    2
                )

                for _ in x

            ]

    }


# ==========================================================
# Benchmark Score
# ==========================================================

def benchmark_score():

    perf = pipeline_performance()

    resources = resource_performance()

    recovery = recovery_metrics()

    score = 100

    score -= perf["latency"] * 0.12

    score -= resources["cpu"] * 0.08

    score -= resources["memory"] * 0.05

    score -= recovery["avg_recovery"] * 2

    score = max(0, min(100, round(score, 1)))

    if score >= 95:

        rating = "Outstanding"

        stars = "★★★★★"

    elif score >= 90:

        rating = "Excellent"

        stars = "★★★★☆"

    elif score >= 80:

        rating = "Good"

        stars = "★★★★"

    elif score >= 70:

        rating = "Fair"

        stars = "★★★"

    else:

        rating = "Needs Improvement"

        stars = "★★"

    return {

        "score": score,

        "rating": rating,

        "stars": stars,

        "generated":

            datetime.now()

    }