import streamlit as st


# ... existing code ...
def render_header():
    """
    Renders the header section of the application with the Capgemini logo and title.
    """
    col1, col2, col3 = st.columns([1, 2, 1])
    with col3:
        st.image("capgemini_logo.png", width=400)  # Adjust the width as needed

    st.markdown(
        "<h1 style='text-align: center;'>CapGenie Regulatory AI Bot</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align: center;'>Regulatory Reporting Center of Excellence AI Initiative</p>",
        unsafe_allow_html=True
    )


def render_home():
    """
    Renders the home page after a successful login, providing navigation options
    for various regulatory reporting functionalities.
    """
    st.markdown(
        "<h2 style='text-align: center; color: #1E3F66;'>Welcome to CapGenie Regulatory Bot</h2>",
        unsafe_allow_html=True
    )
    
    st.markdown("""
    <style>
    .feature-section {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .feature-title {
        color: #1E3F66;
        font-size: 1.2em;
        font-weight: bold;
    }
    .feature-item {
        margin-left: 30px;
    }
    </style>
    
    <div style="text-align: center; color: #4A4A4A;">
        CapGenie Regulatory Bot is an advanced AI-powered solution designed to streamline 
        and enhance your regulatory reporting processes. Our platform offers a comprehensive 
        suite of tools to ensure compliance, accuracy, and efficiency in your reporting tasks.
    </div>
    
    <h3 style="color: #1E3F66; margin-top: 30px;">Key Features:</h3>
    
    <div class="feature-section">
        <p class="feature-title">🔗 Multi-faceted Interaction</p>
        <p class="feature-item">• Database Interaction: Query and analyze regulatory data from various sources.</p>
        <p class="feature-item">• Web Scraping and Analysis: Extract and summarize relevant information from regulatory websites.</p>
        <p class="feature-item">• XBRL Processing: Handle and interpret XBRL documents for financial reporting.</p>
        <p class="feature-item">• Regulatory Report Handling: Manage and process various types of regulatory reports.</p>
    </div>
    
    <div class="feature-section">
        <p class="feature-title">📊 Advanced Analytics</p>
        <p class="feature-item">• Earnings Report Analysis: Automatically extract key insights from financial reports.</p>
        <p class="feature-item">• Scenario Analysis: Simulate different regulatory scenarios and their impacts.</p>
        <p class="feature-item">• Data Validation: Ensure data accuracy and compliance with regulatory standards.</p>
    </div>
    
    <div class="feature-section">
        <p class="feature-title">✅ Compliance Tools</p>
        <p class="feature-item">• Regulatory Calendar: Keep track of important regulatory deadlines and events.</p>
        <p class="feature-item">• Compliance Checklist: Ensure all regulatory requirements are met with interactive checklists.</p>
        <p class="feature-item">• Report Templates: Access and utilize standardized templates for various regulatory reports.</p>
        <p class="feature-item">• Regulatory Q&A: Get instant answers to common regulatory questions.</p>
    </div>
    
    <div class="feature-section">
        <p class="feature-title">🔍 Monitoring and Auditing</p>
        <p class="feature-item">• System Health Dashboard: Monitor the performance and status of your regulatory systems.</p>
        <p class="feature-item">• Audit Trail: Track all actions and changes for compliance and accountability.</p>
        <p class="feature-item">• Session History: Review past interactions and decisions for reference and learning.</p>
    </div>
    
    <div class="feature-section">
        <p class="feature-title">📚 Knowledge Management</p>
        <p class="feature-item">• Interactive Knowledge Base: Access a comprehensive repository of regulatory information.</p>
        <p class="feature-item">• Regulatory News Feed: Stay updated with the latest regulatory news and changes.</p>
    </div>
    
    <div class="feature-section">
        <p class="feature-title">📈 Reporting</p>
        <p class="feature-item">• Customizable Reporting Dashboard: Generate and visualize key regulatory metrics and insights.</p>
    </div>
    
    <div class="feature-section">
        <p class="feature-title">👤 User Management</p>
        <p class="feature-item">• Secure Authentication: Ensure data privacy and user-specific access control.</p>
        <p class="feature-item">• Personalized Settings: Tailor the bot's behavior to individual user preferences.</p>
    </div>
    
    <div style="text-align: center; color: #4A4A4A; margin-top: 30px;">
        This AI-powered tool is designed to streamline your regulatory processes, enhance compliance, and provide valuable insights for financial institutions and regulatory bodies.
    </div>
    
    <div style="text-align: center; color: #1E3F66; font-weight: bold; margin-top: 20px;">
        Navigate through the sidebar to explore the various features and functionalities of the CapGenie Regulatory Bot.
    </div>
    """, unsafe_allow_html=True)

# ... existing code ...
