import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import time

from failure_engine import start_service
from chaos_engine import load_chaos_state, save_chaos_state, tick_chaos, inject_manual_failure
from recovery_engine import tick_recovery, get_recovery_status, recover_manual, get_config, save_config, SERVICE_MAPPINGS
from incident_logger import get_logs
from failure_metrics import calculate_metrics
from health import pipeline_summary

# Map Streamlit UI Names to Container Names
UI_TO_CONTAINER = {
    "Kafka": "kafka",
    "Schema Registry": "schema-registry",
    "Spark Master": "spark-master",
    "Spark Worker": "spark-worker",
    "ClickHouse": "clickhouse",
    "MinIO": "minio",
    "PostgreSQL": "postgres",
    "Airflow Scheduler": "airflow-scheduler",
    "Airflow Webserver": "airflow-webserver",
    "Producer": "producer"
}

def render():
    st.markdown('<h1 style="color:#FF5252;">🚨 Incident & Recovery Center</h1>', unsafe_allow_html=True)
    st.markdown("Monitor pipeline failures, inject chaos testing, and track automated recovery in real-time.")
    
    # Tick background processes
    try:
        tick_chaos()
        tick_recovery()
    except Exception as e:
        st.error(f"Background engines error: {e}. Docker may be unavailable.")
        
    metrics = calculate_metrics()
    
    st.markdown("---")
    
    # ====================================================
    # Section 1: Pipeline Status
    # ====================================================
    st.markdown("### 📊 Pipeline Status")
    
    try:
        pipeline = pipeline_summary()
        healthy_count = pipeline["healthy"]
        total_count = pipeline["total"]
        failed_count = total_count - healthy_count
    except Exception:
        healthy_count = 0
        total_count = 0
        failed_count = 0
        
    recovery_rate = metrics["recovery_percentage"]
    avg_rec_time = metrics["mean_recovery_time"]
    active_incidents = metrics["total_failures"] - metrics["total_recoveries"]
    
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Healthy Services", f"{healthy_count}/{total_count}", delta=f"{-failed_count if failed_count > 0 else 0} Failed", delta_color="inverse")
    with c2:
        st.metric("Active Incidents", active_incidents, delta_color="inverse")
    with c3:
        st.metric("Recovered Incidents", metrics["total_recoveries"])
    with c4:
        st.metric("Recovery Rate", f"{recovery_rate}%")
    with c5:
        st.metric("Avg Recovery Time", f"{avg_rec_time}s")

    st.markdown("---")
    
    # ====================================================
    # Section 2: Failure Injection Panel
    # ====================================================
    st.markdown("### 💥 Failure Injection Panel")
    
    col_fj1, col_fj2, col_fj3 = st.columns([2, 1, 1])
    
    with col_fj1:
        target_service = st.selectbox("Select Service to Inject Failure", list(UI_TO_CONTAINER.keys()))
        
    with col_fj2:
        st.write("") # spacing
        st.write("")
        if st.button("Inject Failure", use_container_width=True, type="primary"):
            container_name = UI_TO_CONTAINER[target_service]
            try:
                success = inject_manual_failure(container_name)
                if success:
                    st.success(f"Successfully stopped {target_service}")
                else:
                    st.error(f"Failed to stop {target_service}. Check if Docker is running.")
            except Exception as e:
                st.error(f"Error: {e}")
                
    with col_fj3:
        st.write("")
        st.write("")
        if st.button("Recover Service", use_container_width=True):
            container_name = UI_TO_CONTAINER[target_service]
            try:
                success = recover_manual(container_name)
                if success:
                    st.success(f"Successfully sent start/restart command to {target_service}")
                else:
                    st.error(f"Failed to restart {target_service}. Check if Docker is running.")
            except Exception as e:
                st.error(f"Error: {e}")
                
    st.markdown("---")
    
    # ====================================================
    # Section 3: Chaos Mode & Config
    # ====================================================
    st.markdown("### 🎲 Chaos Mode")
    
    chaos_state = load_chaos_state()
    config = get_config()
    
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        mode = st.radio("Chaos Mode", ["Disabled", "Manual", "Random"], 
                        index=["Disabled", "Manual", "Random"].index(chaos_state.get("mode", "Disabled")))
        
    with col_c2:
        min_interval = st.number_input("Min Interval (s)", min_value=10, value=config.get("chaos_interval_min", 30))
        max_interval = st.number_input("Max Interval (s)", min_value=10, value=config.get("chaos_interval_max", 90))
        max_retries = st.number_input("Recovery Retries", min_value=1, value=config.get("retry_count", 3))
        
    with col_c3:
        st.write("")
        st.write("")
        if st.button("Save Settings", use_container_width=True):
            chaos_state["mode"] = mode
            chaos_state["enabled"] = mode != "Disabled"
            save_chaos_state(chaos_state)
            
            config["chaos_interval_min"] = min_interval
            config["chaos_interval_max"] = max_interval
            config["retry_count"] = max_retries
            save_config(config)
            st.success("Settings saved successfully.")
    
    st.markdown("---")
    
    # ====================================================
    # Section 5: Recovery Engine
    # ====================================================
    st.markdown("### 🛡️ Recovery Engine Status")
    
    recovery_state = get_recovery_status()
    if not recovery_state:
        st.info("All services are healthy. Recovery Engine is idle.")
    else:
        for svc_name, state in recovery_state.items():
            s_color = "red" if state["status"] == "Failed" else "orange" if state["status"] in ["Restarting", "Waiting"] else "green"
            st.markdown(f"**{svc_name}** | Status: <span style='color:{s_color};'>{state['status']}</span> | Retries: {state['retries']}/{config.get('retry_count', 3)}", unsafe_allow_html=True)
            st.progress(min(state["retries"] / config.get("retry_count", 3), 1.0))
            
    st.markdown("---")
    
    # ====================================================
    # Section 4: Incident Timeline
    # ====================================================
    st.markdown("### ⏳ Incident Timeline")
    logs = get_logs()
    if logs:
        df_logs = pd.DataFrame(logs)
        df_logs["timestamp"] = pd.to_datetime(df_logs["timestamp"]).dt.strftime('%Y-%m-%d %H:%M:%S')
        df_logs["Recovered"] = df_logs["recovered"].apply(lambda x: "✅ Yes" if x else "❌ No")
        df_timeline = df_logs[["timestamp", "service", "failure_type", "severity", "Recovered", "recovery_time"]]
        df_timeline.columns = ["Timestamp", "Service", "Incident", "Severity", "Recovered", "Recovery Time (s)"]
        st.dataframe(df_timeline.tail(10).iloc[::-1], use_container_width=True, hide_index=True)
    else:
        st.info("No incidents recorded yet.")
        
    st.markdown("---")

    # ====================================================
    # Section 6: Metrics Charts
    # ====================================================
    st.markdown("### 📈 Failure Metics")
    if logs and metrics["total_failures"] > 0:
        c1, c2 = st.columns(2)
        
        with c1:
             # Failures by Service Pie Chart
             fail_by_svc = metrics["failures_by_service"]
             df_svc = pd.DataFrame(list(fail_by_svc.items()), columns=["Service", "Count"])
             fig_svc = px.pie(df_svc, values="Count", names="Service", hole=0.4, title="Failures by Service", 
                              color_discrete_sequence=px.colors.sequential.RdBu)
             fig_svc.update_layout(margin=dict(t=30, b=0, l=0, r=0))
             st.plotly_chart(fig_svc, use_container_width=True)
             
        with c2:
             # Recovered vs Failed
             df_rec_status = pd.DataFrame({
                 "Status": ["Recovered", "Pending/Failed"],
                 "Count": [metrics["total_recoveries"], metrics["total_failures"] - metrics["total_recoveries"]]
             })
             fig_rec = px.bar(df_rec_status, x="Status", y="Count", color="Status", title="Recovery Status",
                              color_discrete_map={"Recovered": "#00E676", "Pending/Failed": "#FF5252"})
             fig_rec.update_layout(margin=dict(t=30, b=0, l=0, r=0))
             st.plotly_chart(fig_rec, use_container_width=True)
             
    else:
        st.info("Not enough data to display metrics.")
        
    st.markdown("---")
    
    # ====================================================
    # Section 7: Logs
    # ====================================================
    st.markdown("### 📝 Raw Incident Logs")
    if logs:
        # Display latest 100, newest first
        latest_logs = logs[-100:]
        latest_logs.reverse()
        for l in latest_logs:
            rec_emoji = "✅" if l.get("recovered") else "❌"
            action = l.get("action_taken", "None")
            st.code(f"[{l['timestamp']}] {l['severity']} - {l['service']} : {l['failure_type']} | {rec_emoji} | Action: {action}")
    else:
        st.info("No raw logs available.")
