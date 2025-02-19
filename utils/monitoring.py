import streamlit as st
import psutil
import platform
from datetime import datetime
import plotly.graph_objects as go
import time


def display_system_health():
    """
    Displays a comprehensive and interactive system health dashboard with real-time analytics on various performance metrics.
    """
    # Enhanced Styling with CSS
    st.markdown(
        """
        <style>
        .stMetric {
            font-size: 18px !important;
            color: #007BFF;
        }
        .section-header {
            font-size: 24px;
            font-weight: bold;
            color: #2E86C1;
            margin-top: 20px;
            border-bottom: 2px solid #2E86C1;
            padding-bottom: 10px;
        }
        .system-info, .bot-info, .ai-metrics, .regulatory-metrics {
            background-color: rgba(47, 79, 79, 0.1);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            color: #2E86C1;
            font-size: 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .alert-box {
            border: 1px solid #f8d7da;
            padding: 10px;
            border-radius: 5px;
            background-color: #f8d7da;
            color: #721c24;
        }
        .metric-container {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        .cool-metric {
            background-color: rgba(0, 123, 255, 0.1);
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        .centered {
            text-align: center;
            padding: 0 20%;
        }
        .centered h1 {
            color: #2E86C1;
        }
        </style>
        """, unsafe_allow_html=True
    )

    # Centered title and description
    st.markdown(
        """
        <div class="centered">
            <h1>🤖📊 AI-Powered Regulatory Reporting System Dashboard</h1>
            <p>Real-time analytics on system performance, AI metrics, and regulatory reporting status.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Retrieve system performance metrics
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    disk_usage = psutil.disk_usage('/')
    net_io = psutil.net_io_counters()
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    system_uptime = datetime.now() - boot_time
    battery = psutil.sensors_battery()
    disk_io = psutil.disk_io_counters()
    swap_info = psutil.swap_memory()
    cpu_freq = psutil.cpu_freq()

    # Displaying basic system metrics
    st.markdown('<div class="section-header">🔑 Key Performance Metrics</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="CPU Usage", value=f"{cpu_usage}%", delta=f"{cpu_usage - 50:.1f}%", help="Current CPU usage")
    col2.metric(label="Memory Usage", value=f"{memory_info.percent}%", delta=f"{memory_info.percent - 40:.1f}%",
                help="Current Memory usage")
    col3.metric(label="Disk Usage", value=f"{disk_usage.percent}%", delta=f"{disk_usage.percent - 60:.1f}%",
                help="Current Disk usage")
    col4.metric(label="Swap Usage", value=f"{swap_info.percent}%", delta=f"{swap_info.percent - 20:.1f}%",
                help="Current Swap usage")

    # Network and Disk I/O metrics
    st.markdown('<div class="section-header">📶 Network and Disk I/O Activity</div>', unsafe_allow_html=True)
    st.write(f"**Network Sent:** {get_size(net_io.bytes_sent)} | **Received:** {get_size(net_io.bytes_recv)}")
    st.write(f"**Disk Read:** {get_size(disk_io.read_bytes)} | **Disk Write:** {get_size(disk_io.write_bytes)}")

    # CPU frequency details
    st.markdown('<div class="section-header">⚙️ CPU Frequency</div>', unsafe_allow_html=True)
    st.write(
        f"**Current:** {cpu_freq.current:.2f} MHz | **Min:** {cpu_freq.min:.2f} MHz | **Max:** {cpu_freq.max:.2f} MHz")

    # System uptime
    st.markdown('<div class="section-header">⏰ System Uptime</div>', unsafe_allow_html=True)
    st.write(f"**System has been up for:** {str(system_uptime).split('.')[0]}")

    # Battery status
    if battery:
        battery_status = f"{battery.percent}% ({'Plugged In' if battery.power_plugged else 'Not Plugged In'})"
        st.metric(label="Battery Status", value=battery_status)
    else:
        st.write("Battery information not available.")

    # System information
    st.markdown('<div class="section-header">💻 System Information</div>', unsafe_allow_html=True)
    os_name = platform.system()
    os_release = platform.release()
    processor = platform.processor()
    cpu_count = psutil.cpu_count(logical=True)
    architecture = platform.architecture()[0]
    machine = platform.machine()
    node = platform.node()
    python_version = platform.python_version()

    st.markdown(
        f"""
        <div class="system-info">
            <b>Operating System:</b> {os_name} {os_release}<br>
            <b>Processor:</b> {processor} ({cpu_count} cores)<br>
            <b>Architecture:</b> {architecture}<br>
            <b>Machine Type:</b> {machine}<br>
            <b>Hostname:</b> {node}<br>
            <b>Python Version:</b> {python_version}
        </div>
        """, unsafe_allow_html=True
    )

    # AI and Machine Learning Metrics
    st.markdown('<div class="section-header">🧠 AI and ML Performance Metrics</div>', unsafe_allow_html=True)

    # Mock data for AI metrics (replace with real data in production)
    model_accuracy = 95.5
    inference_time = 120  # ms
    active_models = 3
    data_processed = 1250000  # rows

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Model Accuracy", value=f"{model_accuracy}%", delta="1.5%")
    col2.metric(label="Avg Inference Time", value=f"{inference_time} ms", delta="-10 ms")
    col3.metric(label="Active Models", value=active_models)
    col4.metric(label="Data Processed", value=f"{data_processed:,} rows")

    st.markdown(
        """
        <div class="ai-metrics">
            <b>Latest Model Version:</b> v2.3.1<br>
            <b>Training Dataset:</b> Q2 2024 Financial Reports<br>
            <b>Last Retraining:</b> 2024-03-15 09:30:00 UTC<br>
            <b>Feature Importance:</b> Revenue (0.3), Assets (0.25), Liabilities (0.2), Cash Flow (0.15), Market Cap (0.1)
        </div>
        """, unsafe_allow_html=True
    )

    # Regulatory Reporting Metrics
    st.markdown('<div class="section-header">📋 Regulatory Reporting Status</div>', unsafe_allow_html=True)

    # Mock data for regulatory metrics (replace with real data in production)
    reports_generated = 150
    compliance_score = 98.5
    pending_reviews = 5
    avg_processing_time = 25  # minutes

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Reports Generated", value=reports_generated, delta="10")
    col2.metric(label="Compliance Score", value=f"{compliance_score}%", delta="0.5%")
    col3.metric(label="Pending Reviews", value=pending_reviews, delta="-2")
    col4.metric(label="Avg Processing Time", value=f"{avg_processing_time} min", delta="-5 min")

    st.markdown(
        """
        <div class="regulatory-metrics">
            <b>Latest Regulation Update:</b> Basel III - 2024-02-01<br>
            <b>Next Reporting Deadline:</b> 2024-04-30 (Quarterly Financial Statements)<br>
            <b>Top Compliance Flags:</b> Liquidity Risk (3), Credit Exposure (2), Operational Risk (1)<br>
            <b>Auditor Notes:</b> All critical metrics within acceptable ranges. Minor improvements suggested for operational risk assessment.
        </div>
        """, unsafe_allow_html=True
    )

    # Cool Additional Metrics
    st.markdown('<div class="section-header">🚀 Advanced Analytics</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="cool-metric">
                <h4>AI Model Health Score</h4>
                <div style="font-size: 24px; font-weight: bold; color: #00ff00;">92/100</div>
                <small>Based on accuracy, latency, and data quality</small>
            </div>
            """, unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="cool-metric">
                <h4>Regulatory Compliance Forecast</h4>
                <div style="font-size: 24px; font-weight: bold; color: #00ff00;">Low Risk</div>
                <small>Predicted compliance status for next quarter</small>
            </div>
            """, unsafe_allow_html=True
        )

    # Interactive and compact performance trends using Plotly
    st.markdown('<div class="section-header">📈 Compact Performance Trends</div>', unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[datetime.now()], y=[cpu_usage], mode='lines+markers', name='CPU Usage',
                             line=dict(color='firebrick')))
    fig.add_trace(go.Scatter(x=[datetime.now()], y=[memory_info.percent], mode='lines+markers', name='Memory Usage',
                             line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=[datetime.now()], y=[disk_usage.percent], mode='lines+markers', name='Disk Usage',
                             line=dict(color='green')))
    fig.update_layout(
        autosize=True,
        height=250,
        margin=dict(l=20, r=20, t=20, b=20),
        hovermode="x unified",
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Advanced analytics with conditional warnings
    st.markdown('<div class="section-header">⚠️ System Alerts</div>', unsafe_allow_html=True)
    alerts = []
    if cpu_usage > 80:
        alerts.append("⚠️ **High CPU Usage Detected:** CPU usage exceeds 80%")
    if memory_info.percent > 80:
        alerts.append("⚠️ **High Memory Usage Detected:** Memory usage exceeds 80%")
    if disk_usage.percent > 90:
        alerts.append("⚠️ **High Disk Usage Detected:** Disk usage exceeds 90%")
    if swap_info.percent > 80:
        alerts.append("⚠️ **High Swap Usage Detected:** Swap usage exceeds 80%")

    if alerts:
        for alert in alerts:
            st.markdown(f'<div class="alert-box">{alert}</div>', unsafe_allow_html=True)
    else:
        st.success("✅ System performance is within normal ranges.")

    # Recent AI Insights
    st.markdown('<div class="section-header">💡 Recent AI Insights</div>', unsafe_allow_html=True)
    ai_insights = [
        "Detected potential anomaly in Q3 revenue projections",
        "Suggested optimization for credit risk assessment model",
        "Identified emerging trend in market liquidity patterns"
    ]
    for insight in ai_insights:
        st.write(f"- {insight}")


def get_size(bytes, suffix="B"):
    """
    Scale bytes to a more readable format (e.g., KB, MB, GB).
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


def refresh_performance_metrics():
    """
    Refreshes the performance metrics displayed in the system health dashboard.
    """
    with st.spinner("Refreshing performance metrics..."):
        display_system_health()
        time.sleep(1)  # Simulate a short delay for refreshing