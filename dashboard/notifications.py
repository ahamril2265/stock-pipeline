import streamlit as st

from health import pipeline_summary
from db import (
    get_market_kpis,
    get_top_symbols
)

from config import (
    LATENCY_THRESHOLD,
    PRICE_SPIKE_PERCENT,
    VOLUME_SPIKE
)


# ==========================================================
# Generate Alerts
# ==========================================================

def get_notifications():

    alerts = []

    # ------------------------------------------
    # Infrastructure
    # ------------------------------------------

    pipeline = pipeline_summary()

    services = pipeline["services"]

    resources = pipeline["resources"]

    for service, status in services.items():

        if not status:

            alerts.append({

                "level": "error",

                "title": f"{service} Offline",

                "message": f"{service} is unreachable."

            })

    # ------------------------------------------
    # Resources
    # ------------------------------------------

    if resources["cpu"] > 90:

        alerts.append({

            "level": "warning",

            "title": "High CPU Usage",

            "message": f"CPU utilization is {resources['cpu']}%."

        })

    if resources["memory"] > 90:

        alerts.append({

            "level": "warning",

            "title": "High Memory Usage",

            "message": f"Memory utilization is {resources['memory']}%."

        })

    if resources["disk"] > 90:

        alerts.append({

            "level": "error",

            "title": "Disk Almost Full",

            "message": f"Disk usage is {resources['disk']}%."

        })

    # ------------------------------------------
    # Market KPIs
    # ------------------------------------------

    market = get_market_kpis()

    if not market.empty:

        row = market.iloc[0]

        if row["avg_market_latency"] > LATENCY_THRESHOLD:

            alerts.append({

                "level": "warning",

                "title": "High Market Latency",

                "message":
                f"{row['avg_market_latency']:.2f} ms"

            })

    # ------------------------------------------
    # Top Symbols
    # ------------------------------------------

    symbols = get_top_symbols()

    if not symbols.empty:

        for _, row in symbols.iterrows():

            if row["total_volume"] > VOLUME_SPIKE:

                alerts.append({

                    "level": "info",

                    "title": "Volume Spike",

                    "message":
                    f"{row['stock_symbol']} volume exceeded threshold."

                })

    return alerts


# ==========================================================
# Notification Center
# ==========================================================

def render_notifications():

    alerts = get_notifications()

    st.subheader("🔔 Notification Center")

    if not alerts:

        st.success(
            "✅ No active alerts."
        )

        return

    for alert in alerts:

        if alert["level"] == "error":

            st.error(

                f"🚨 **{alert['title']}**\n\n"

                f"{alert['message']}"

            )

        elif alert["level"] == "warning":

            st.warning(

                f"⚠ **{alert['title']}**\n\n"

                f"{alert['message']}"

            )

        else:

            st.info(

                f"ℹ **{alert['title']}**\n\n"

                f"{alert['message']}"

            )


# ==========================================================
# Compact Header Notifications
# ==========================================================

def notification_badge():

    alerts = get_notifications()

    errors = sum(

        a["level"] == "error"

        for a in alerts

    )

    warnings = sum(

        a["level"] == "warning"

        for a in alerts

    )

    infos = sum(

        a["level"] == "info"

        for a in alerts

    )

    return {

        "errors": errors,

        "warnings": warnings,

        "infos": infos,

        "total": len(alerts)

    }