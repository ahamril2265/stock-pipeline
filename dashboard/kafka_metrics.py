from kafka import KafkaAdminClient
from kafka.errors import KafkaError

import socket


# ==========================================================
# Configuration
# ==========================================================

KAFKA_BOOTSTRAP = "kafka:29092"


# ==========================================================
# Broker Health
# ==========================================================

def broker_alive():

    try:

        host, port = KAFKA_BOOTSTRAP.split(":")

        sock = socket.create_connection(
            (host, int(port)),
            timeout=3
        )

        sock.close()

        return True

    except Exception:

        return False


# ==========================================================
# Admin Client
# ==========================================================

def admin():

    try:

        return KafkaAdminClient(
            bootstrap_servers=KAFKA_BOOTSTRAP,
            client_id="dashboard"
        )

    except Exception:

        return None


# ==========================================================
# Topics
# ==========================================================

def topics():

    client = admin()

    if client is None:
        return []

    try:

        output = []

        metadata = client.describe_topics(
            client.list_topics()
        )

        for topic in metadata:

            output.append({

                "Topic":
                    topic["topic"],

                "Partitions":
                    len(topic["partitions"]),

                "Internal":
                    topic["is_internal"]

            })

        return sorted(
            output,
            key=lambda x: x["Topic"]
        )

    except Exception:

        return []


# ==========================================================
# Cluster Summary
# ==========================================================

def cluster_summary():

    client = admin()

    if client is None:
        return None

    try:

        metadata = client.describe_topics(
            client.list_topics()
        )

        partitions = sum(
            len(topic["partitions"])
            for topic in metadata
        )

        internal = sum(
            topic["is_internal"]
            for topic in metadata
        )

        return {

            "broker":
                "ONLINE",

            "topics":
                len(metadata),

            "partitions":
                partitions,

            "internal_topics":
                internal,

            "user_topics":
                len(metadata) - internal

        }

    except Exception:

        return None


# ==========================================================
# Topic Details
# ==========================================================

def topic_statistics():

    client = admin()

    if client is None:
        return []

    try:

        metadata = client.describe_topics(
            client.list_topics()
        )

        output = []

        for topic in metadata:

            replicas = 0

            leaders = 0

            for p in topic["partitions"]:

                replicas += len(
                    p["replicas"]
                )

                if p["leader"] >= 0:
                    leaders += 1

            output.append({

                "Topic":
                    topic["topic"],

                "Partitions":
                    len(topic["partitions"]),

                "Leaders":
                    leaders,

                "Replicas":
                    replicas,

                "Internal":
                    topic["is_internal"]

            })

        return output

    except Exception:

        return []


# ==========================================================
# Cluster Health
# ==========================================================

def cluster_health():

    summary = cluster_summary()

    if summary is None:

        return {

            "healthy": False

        }

    return {

        "healthy": True,

        "broker":
            summary["broker"],

        "topics":
            summary["topics"],

        "partitions":
            summary["partitions"]

    }

# ==========================================================
# Backward Compatibility
# ==========================================================

def kafka_metrics():

    return {

        "summary": cluster_summary(),

        "health": cluster_health(),

        "topics": topic_statistics()

    }