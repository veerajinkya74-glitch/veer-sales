import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import io
import base64
import os

# ========================= PAGE CONFIG =========================
st.set_page_config(
    page_title="Veer Sales & Services",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================= GLOBAL CSS =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700;800&family=Playfair+Display:wght@700&display=swap');

/* ── Root variables ── */
:root {
    --blue-deep:   #0a2342;
    --blue-mid:    #1a3a5c;
    --blue-bright: #1565c0;
    --blue-light:  #42a5f5;
    --blue-glass:  rgba(21,101,192,0.12);
    --cyan:        #00bcd4;
    --white:       #ffffff;
    --off-white:   #f0f6ff;
    --text-main:   #0d1b2a;
    --text-muted:  #546e7a;
    --success:     #00c853;
    --warning:     #ffd600;
    --danger:      #f44336;
    --card-shadow: 0 8px 32px rgba(10,35,66,0.13);
    --radius:      16px;
}

/* ── Animated water background ── */
.stApp {
    background: linear-gradient(135deg, #e8f4fd 0%, #dbeeff 30%, #e3f2fd 60%, #e8f5f8 100%);
    font-family: 'Nunito', sans-serif;
    color: var(--text-main);
    min-height: 100vh;
    position: relative;
}

/* Animated wave blobs */
.stApp::before {
    content: '';
    position: fixed;
    top: -120px; left: -120px;
    width: 600px; height: 600px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(66,165,245,0.18) 0%, rgba(21,101,192,0.06) 60%, transparent 80%);
    animation: drift1 12s ease-in-out infinite alternate;
    pointer-events: none; z-index: 0;
}
.stApp::after {
    content: '';
    position: fixed;
    bottom: -100px; right: -100px;
    width: 500px; height: 500px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0,188,212,0.15) 0%, rgba(21,101,192,0.05) 60%, transparent 80%);
    animation: drift2 15s ease-in-out infinite alternate;
    pointer-events: none; z-index: 0;
}
@keyframes drift1 { 0%{transform:translate(0,0) scale(1)} 100%{transform:translate(60px,40px) scale(1.12)} }
@keyframes drift2 { 0%{transform:translate(0,0) scale(1)} 100%{transform:translate(-50px,-30px) scale(1.1)} }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--blue-deep) 0%, var(--blue-mid) 100%) !important;
    border-right: none !important;
    box-shadow: 4px 0 24px rgba(10,35,66,0.18);
    overflow-x: hidden !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 16px !important;
}
[data-testid="stSidebar"] * { color: var(--white) !important; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label { color: rgba(255,255,255,0.85) !important; }

/* Fix sidebar info/footer overlapping */
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: rgba(255,255,255,0.6) !important;
    font-size: 11px !important;
    line-height: 1.5 !important;
    word-break: break-word !important;
}

/* Sidebar selectbox */
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    color: white !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] svg { color: white !important; fill: white !important; }

/* Hide Streamlit default sidebar header padding */
[data-testid="stSidebarHeader"] { display: none !important; }
section[data-testid="stSidebar"] > div { padding-top: 0 !important; }

/* ── Logo area ── */
.logo-container {
    display: flex; align-items: center; gap: 14px;
    padding: 8px 0 20px 0;
    border-bottom: 1px solid rgba(255,255,255,0.15);
    margin-bottom: 20px;
}
.logo-icon {
    width: 54px; height: 54px;
    background: linear-gradient(135deg, var(--cyan), var(--blue-bright));
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 26px; box-shadow: 0 4px 14px rgba(0,188,212,0.4);
    flex-shrink: 0;
}
.logo-text-main {
    font-family: 'Playfair Display', serif;
    font-size: 18px; font-weight: 700;
    color: white; line-height: 1.1;
}
.logo-text-sub {
    font-size: 11px; color: rgba(255,255,255,0.6);
    letter-spacing: 1px; text-transform: uppercase;
}

/* ── Page title ── */
.page-header {
    background: linear-gradient(135deg, var(--blue-deep) 0%, var(--blue-mid) 100%);
    border-radius: var(--radius);
    padding: 24px 32px;
    margin-bottom: 28px;
    box-shadow: var(--card-shadow);
    display: flex; align-items: center; gap: 16px;
}
.page-header h1 {
    font-family: 'Playfair Display', serif;
    font-size: 28px; color: white; margin: 0; font-weight: 700;
}
.page-header p { color: rgba(255,255,255,0.7); margin: 4px 0 0 0; font-size: 14px; }

/* ── Metric cards ── */
.metric-row { display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }
.metric-card {
    flex: 1; min-width: 160px;
    background: white;
    border-radius: var(--radius);
    padding: 22px 24px;
    box-shadow: var(--card-shadow);
    border-top: 4px solid;
    position: relative; overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}
.metric-card:hover { transform: translateY(-3px); box-shadow: 0 16px 40px rgba(10,35,66,0.18); }
.metric-card::after {
    content: ''; position: absolute;
    bottom: -20px; right: -20px;
    width: 90px; height: 90px;
    border-radius: 50%;
    background: currentColor; opacity: 0.05;
}
.metric-card.blue  { border-color: var(--blue-bright); color: var(--blue-bright); }
.metric-card.red   { border-color: var(--danger);      color: var(--danger); }
.metric-card.amber { border-color: var(--warning);     color: #f57f17; }
.metric-card.teal  { border-color: var(--cyan);        color: #00838f; }
.metric-label { font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; opacity: 0.75; }
.metric-value { font-size: 42px; font-weight: 800; line-height: 1.1; margin: 4px 0 0; }
.metric-icon  { font-size: 22px; position: absolute; top: 20px; right: 20px; opacity: 0.5; }

/* ── Glass cards ── */
.glass-card {
    background: rgba(255,255,255,0.82);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.9);
    border-radius: var(--radius);
    padding: 24px 28px;
    box-shadow: var(--card-shadow);
    margin-bottom: 20px;
}

/* ── Section heading ── */
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 20px; font-weight: 700;
    color: var(--blue-deep); margin: 0 0 16px;
    padding-bottom: 10px;
    border-bottom: 2px solid rgba(21,101,192,0.12);
}

/* ── Status badges ── */
.badge {
    display: inline-block; padding: 3px 12px;
    border-radius: 20px; font-size: 12px; font-weight: 700;
    letter-spacing: 0.5px;
}
.badge-green  { background: #e8f5e9; color: #2e7d32; }
.badge-red    { background: #ffebee; color: #c62828; }
.badge-amber  { background: #fff8e1; color: #e65100; }
.badge-blue   { background: #e3f2fd; color: #1565c0; }

/* ── Form styling ── */
[data-testid="stForm"] {
    background: rgba(255,255,255,0.85);
    border: 1px solid rgba(21,101,192,0.12);
    border-radius: var(--radius);
    padding: 24px !important;
    box-shadow: var(--card-shadow);
}
.stTextInput input, .stSelectbox select, .stTextArea textarea {
    border-radius: 10px !important;
    border: 1.5px solid rgba(21,101,192,0.2) !important;
    font-family: 'Nunito', sans-serif !important;
    transition: border-color 0.2s !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--blue-bright) !important;
    box-shadow: 0 0 0 3px rgba(21,101,192,0.1) !important;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 10px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.3px !important;
    transition: all 0.2s !important;
    border: none !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--blue-bright), var(--blue-light)) !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(21,101,192,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 20px rgba(21,101,192,0.4) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.6) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid rgba(21,101,192,0.1) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    color: var(--text-muted) !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--blue-bright), var(--blue-light)) !important;
    color: white !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

/* ── Alerts ── */
.stSuccess, .stInfo, .stWarning, .stError { border-radius: 10px !important; }

/* ── Divider ── */
hr { border-color: rgba(21,101,192,0.1) !important; }

/* ── Alert cards ── */
.alert-card {
    display: flex; align-items: flex-start; gap: 14px;
    padding: 14px 18px; border-radius: 12px;
    margin-bottom: 10px;
    border-left: 4px solid;
}
.alert-card.overdue   { background: #fff5f5; border-color: var(--danger); }
.alert-card.due-soon  { background: #fffde7; border-color: var(--warning); }
.alert-card.expiring  { background: #e3f2fd; border-color: var(--blue-bright); }
.alert-card .alert-title { font-weight: 700; font-size: 14px; margin: 0; }
.alert-card .alert-sub   { font-size: 12px; color: var(--text-muted); margin: 2px 0 0; }

/* ── Watermark pattern ── */
.watermark {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    pointer-events: none; z-index: 0; opacity: 0.025;
    background-image: radial-gradient(circle, #1565c0 1px, transparent 1px);
    background-size: 40px 40px;
}
</style>

<div class="watermark"></div>
""", unsafe_allow_html=True)

# ========================= DATABASE =========================
@st.cache_resource
def get_connection():
    conn = sqlite3.connect('water_purifier.db', check_same_thread=False)
    conn.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, phone TEXT, address TEXT, model TEXT,
        purchase_date TEXT, contract_start TEXT, contract_end TEXT,
        last_service TEXT, next_service TEXT,
        payment_status TEXT DEFAULT 'Pending',
        notes TEXT
    )''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS service_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        service_date TEXT,
        service_type TEXT,
        technician TEXT,
        cost REAL,
        notes TEXT,
        FOREIGN KEY(customer_id) REFERENCES customers(id)
    )''')
    conn.commit()
    return conn

conn = get_connection()

def load_customers():
    return pd.read_sql("SELECT * FROM customers", conn)

def load_service_records():
    return pd.read_sql("""
        SELECT sr.*, c.name as customer_name, c.model
        FROM service_records sr
        LEFT JOIN customers c ON sr.customer_id = c.id
        ORDER BY sr.service_date DESC
    """, conn)

# ========================= SIDEBAR =========================
# Logo
if os.path.exists("logo.png"):
    with open("logo.png", "rb") as f:
        logo_data = base64.b64encode(f.read()).decode()
    st.sidebar.markdown(f"""
    <div class="logo-container">
        <img src="data:image/png;base64,{logo_data}" style="width:54px;height:54px;border-radius:14px;object-fit:contain;background:white;padding:4px;">
        <div>
            <div class="logo-text-main">Veer Sales</div>
            <div class="logo-text-sub">& Services</div>
        </div>
    </div>""", unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
    <div class="logo-container">
        <div class="logo-icon">💧</div>
        <div>
            <div class="logo-text-main">Veer Sales</div>
            <div class="logo-text-sub">& Services</div>
        </div>
    </div>""", unsafe_allow_html=True)

st.sidebar.markdown("### 📋 Navigation")
menu = st.sidebar.selectbox("", [
    "📊 Dashboard",
    "➕ Add Customer",
    "👥 All Customers",
    "⏰ Service Reminders",
    "🔧 Add Service Record",
    "📈 Reports & Analytics",
    "📥 Export & Backup",
    "⚙️ Settings"
], label_visibility="collapsed")

today = datetime.today().date()

# Sidebar quick stats
df_all = load_customers()
if not df_all.empty:
    df_all['next_service'] = pd.to_datetime(df_all['next_service'], errors='coerce').dt.date
    overdue = len(df_all[df_all['next_service'] < today])
    st.sidebar.markdown(f"""
    <div style="margin-top:24px;padding:16px;background:rgba(255,255,255,0.08);border-radius:12px;border:1px solid rgba(255,255,255,0.15)">
        <div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;color:rgba(255,255,255,0.6);margin-bottom:10px">Quick Stats</div>
        <div style="display:flex;justify-content:space-between;margin-bottom:6px">
            <span style="font-size:13px;color:rgba(255,255,255,0.8)">Total Customers</span>
            <span style="font-weight:800;color:#42a5f5">{len(df_all)}</span>
        </div>
        <div style="display:flex;justify-content:space-between">
            <span style="font-size:13px;color:rgba(255,255,255,0.8)">Overdue Services</span>
            <span style="font-weight:800;color:#f44336">{overdue}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("""
<div style="margin-top:32px;padding:12px;text-align:center;font-size:11px;color:rgba(255,255,255,0.35);border-top:1px solid rgba(255,255,255,0.08)">
    💾 Local SQLite • v2.0<br>Veer Sales &amp; Services
</div>
""", unsafe_allow_html=True)

# ========================= HELPER =========================
def page_header(icon, title, subtitle=""):
    st.markdown(f"""
    <div class="page-header">
        <div style="font-size:36px">{icon}</div>
        <div>
            <h1>{title}</h1>
            {"<p>" + subtitle + "</p>" if subtitle else ""}
        </div>
    </div>""", unsafe_allow_html=True)

# ========================= DASHBOARD =========================
if menu == "📊 Dashboard":
    page_header("📊", "Dashboard Overview", "Real-time snapshot of your business")

    df = load_customers()
    if not df.empty:
        df['next_service']  = pd.to_datetime(df['next_service'],  errors='coerce').dt.date
        df['contract_end']  = pd.to_datetime(df['contract_end'],  errors='coerce').dt.date
        df['purchase_date'] = pd.to_datetime(df['purchase_date'], errors='coerce').dt.date

        total       = len(df)
        overdue     = len(df[df['next_service'] < today])
        due_30      = len(df[(df['next_service'] >= today) & (df['next_service'] <= today + timedelta(days=30))])
        exp_60      = len(df[df['contract_end'] <= today + timedelta(days=60)])

        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-card blue">
                <div class="metric-label">Total Customers</div>
                <div class="metric-value">{total}</div>
                <div class="metric-icon">👥</div>
            </div>
            <div class="metric-card red">
                <div class="metric-label">Overdue Services</div>
                <div class="metric-value">{overdue}</div>
                <div class="metric-icon">🔴</div>
            </div>
            <div class="metric-card amber">
                <div class="metric-label">Due in 30 Days</div>
                <div class="metric-value">{due_30}</div>
                <div class="metric-icon">⏰</div>
            </div>
            <div class="metric-card teal">
                <div class="metric-label">Contracts Expiring</div>
                <div class="metric-value">{exp_60}</div>
                <div class="metric-icon">⚠️</div>
            </div>
        </div>""", unsafe_allow_html=True)

        # Charts row
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<p class="section-title">💧 Purifier Models Distribution</p>', unsafe_allow_html=True)
            model_counts = df['model'].value_counts().reset_index()
            model_counts.columns = ['Model', 'Count']
            fig = px.pie(model_counts, values='Count', names='Model',
                         color_discrete_sequence=px.colors.sequential.Blues_r,
                         hole=0.4)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False, height=280
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<p class="section-title">📅 Payment Status Breakdown</p>', unsafe_allow_html=True)
            if 'payment_status' in df.columns:
                pay_counts = df['payment_status'].value_counts().reset_index()
                pay_counts.columns = ['Status', 'Count']
                colors = {'Paid': '#00c853', 'Pending': '#ffd600', 'Overdue': '#f44336'}
                fig2 = px.bar(pay_counts, x='Status', y='Count',
                              color='Status',
                              color_discrete_map=colors,
                              text='Count')
                fig2.update_traces(textposition='outside')
                fig2.update_layout(
                    margin=dict(t=10, b=10, l=10, r=10),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    showlegend=False, height=280,
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
                )
                st.plotly_chart(fig2, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Recent customers
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">🆕 Recent Customers</p>', unsafe_allow_html=True)
        recent = df.sort_values('purchase_date', ascending=False).head(5)[
            ['name', 'phone', 'model', 'payment_status', 'next_service']
        ].reset_index(drop=True)
        st.dataframe(recent, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="glass-card" style="text-align:center;padding:60px">
            <div style="font-size:60px;margin-bottom:16px">💧</div>
            <h3 style="color:#1565c0;font-family:'Playfair Display',serif">No customers yet!</h3>
            <p style="color:#546e7a">Add your first customer to see the dashboard come alive.</p>
        </div>""", unsafe_allow_html=True)

# ========================= ADD CUSTOMER =========================
elif menu == "➕ Add Customer":
    page_header("➕", "Add New Customer", "Register a new water purifier installation")

    with st.form("add_form", clear_on_submit=True):
        st.markdown('<p class="section-title">👤 Customer Information</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            name  = st.text_input("Customer Name *", placeholder="e.g. Rahul Sharma")
            phone = st.text_input("Phone Number *",  placeholder="+91 98765 43210")
            model = st.text_input("Purifier Model",  placeholder="e.g. Kent Grand, Aquaguard Aura")
            payment_status = st.selectbox("Payment Status", ["Paid", "Pending", "Overdue"])
        with col2:
            purchase_date   = st.date_input("Purchase Date",              datetime.today())
            contract_start  = st.date_input("Annual Contract Start Date", datetime.today())
            last_service    = st.date_input("Last Service Date",          datetime.today())
            service_interval= st.selectbox("Next Service In", ["3 Months", "6 Months", "1 Year"])

        address = st.text_area("Full Address", placeholder="Building, Street, Area, City, PIN")
        notes   = st.text_area("Notes / Remarks", placeholder="Any special instructions...")

        submitted = st.form_submit_button("💾 Save Customer", type="primary", use_container_width=True)
        if submitted:
            if not name or not phone:
                st.error("⚠️ Customer Name and Phone are required!")
            else:
                contract_end = contract_start + timedelta(days=365)
                days_map = {"3 Months": 90, "6 Months": 180, "1 Year": 365}
                next_service = last_service + timedelta(days=days_map[service_interval])
                conn.execute('''INSERT INTO customers VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?)''',
                    (name, phone, address, model, str(purchase_date), str(contract_start),
                     str(contract_end), str(last_service), str(next_service), payment_status, notes))
                conn.commit()
                st.success(f"✅ Customer **{name}** saved successfully!")
                st.balloons()

# ========================= ALL CUSTOMERS =========================
elif menu == "👥 All Customers":
    page_header("👥", "All Customers", "View, search, edit and delete customer records")

    df = load_customers()
    if not df.empty:
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            search = st.text_input("🔍 Search by name or phone", placeholder="Type to search...")
        with col2:
            filter_payment = st.selectbox("Filter by Payment", ["All", "Paid", "Pending", "Overdue"])
        with col3:
            filter_model = st.selectbox("Filter by Model", ["All"] + sorted(df['model'].dropna().unique().tolist()))

        filtered = df.copy()
        if search:
            filtered = filtered[
                filtered['name'].str.contains(search, case=False, na=False) |
                filtered['phone'].str.contains(search, case=False, na=False)
            ]
        if filter_payment != "All":
            filtered = filtered[filtered['payment_status'] == filter_payment]
        if filter_model != "All":
            filtered = filtered[filtered['model'] == filter_model]

        st.markdown(f'<p style="color:#546e7a;font-size:13px;margin-bottom:8px">Showing <b>{len(filtered)}</b> of <b>{len(df)}</b> customers</p>', unsafe_allow_html=True)

        display_cols = ['id', 'name', 'phone', 'model', 'payment_status', 'next_service', 'contract_end']
        st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True,
                     column_config={
                         "id":             st.column_config.NumberColumn("ID", width="small"),
                         "name":           st.column_config.TextColumn("Customer Name"),
                         "phone":          st.column_config.TextColumn("Phone"),
                         "model":          st.column_config.TextColumn("Model"),
                         "payment_status": st.column_config.TextColumn("Payment"),
                         "next_service":   st.column_config.DateColumn("Next Service"),
                         "contract_end":   st.column_config.DateColumn("Contract Ends"),
                     })

        st.markdown("---")
        st.markdown('<p class="section-title">✏️ Edit or Delete Customer</p>', unsafe_allow_html=True)

        cust_options = df['name'] + " — " + df['phone']
        selected = st.selectbox("Select Customer", cust_options)
        cust_row = df[cust_options == selected].iloc[0]
        cust_id  = int(cust_row['id'])

        with st.expander("📝 Edit Customer Details", expanded=False):
            with st.form("edit_form"):
                col1, col2 = st.columns(2)
                with col1:
                    e_name    = st.text_input("Name",   value=cust_row['name'])
                    e_phone   = st.text_input("Phone",  value=cust_row['phone'])
                    e_model   = st.text_input("Model",  value=cust_row['model'] or "")
                    e_payment = st.selectbox("Payment Status", ["Paid", "Pending", "Overdue"],
                                             index=["Paid","Pending","Overdue"].index(cust_row['payment_status']) if cust_row['payment_status'] in ["Paid","Pending","Overdue"] else 1)
                with col2:
                    e_last    = st.date_input("Last Service", pd.to_datetime(cust_row['last_service']).date() if cust_row['last_service'] else today)
                    e_next    = st.date_input("Next Service", pd.to_datetime(cust_row['next_service']).date() if cust_row['next_service'] else today)
                    e_cend    = st.date_input("Contract End", pd.to_datetime(cust_row['contract_end']).date() if cust_row['contract_end'] else today)
                e_address = st.text_area("Address", value=cust_row['address'] or "")
                e_notes   = st.text_area("Notes",   value=cust_row['notes'] or "")
                if st.form_submit_button("💾 Update Customer", type="primary"):
                    conn.execute("""UPDATE customers SET name=?,phone=?,address=?,model=?,
                                    last_service=?,next_service=?,contract_end=?,payment_status=?,notes=?
                                    WHERE id=?""",
                                 (e_name, e_phone, e_address, e_model, str(e_last), str(e_next),
                                  str(e_cend), e_payment, e_notes, cust_id))
                    conn.commit()
                    st.success("✅ Customer updated!")
                    st.rerun()

        if st.button("🗑️ Delete This Customer", type="primary"):
            conn.execute("DELETE FROM customers WHERE id=?", (cust_id,))
            conn.commit()
            st.success("Customer deleted.")
            st.rerun()
    else:
        st.info("No customers yet. Add one from the menu.")

# ========================= SERVICE REMINDERS =========================
elif menu == "⏰ Service Reminders":
    page_header("⏰", "Service Reminders", "Stay ahead of every service and contract renewal")

    df = load_customers()
    if not df.empty:
        df['next_service'] = pd.to_datetime(df['next_service'], errors='coerce').dt.date
        df['contract_end'] = pd.to_datetime(df['contract_end'], errors='coerce').dt.date

        tab1, tab2, tab3 = st.tabs(["🔴 Overdue", "🟡 Due in 30 Days", "📋 Contract Expiring"])

        with tab1:
            overdue_df = df[df['next_service'] < today].sort_values('next_service')
            if not overdue_df.empty:
                for _, row in overdue_df.iterrows():
                    days_late = (today - row['next_service']).days
                    st.markdown(f"""
                    <div class="alert-card overdue">
                        <div style="font-size:22px">🔴</div>
                        <div>
                            <p class="alert-title">{row['name']} — {row['phone']}</p>
                            <p class="alert-sub">📱 Model: {row['model'] or 'N/A'} &nbsp;|&nbsp; 
                               🗓️ Due: {row['next_service']} &nbsp;|&nbsp; 
                               ⚠️ <b>{days_late} days overdue</b></p>
                        </div>
                    </div>""", unsafe_allow_html=True)
            else:
                st.success("🎉 No overdue services!")

        with tab2:
            soon_df = df[(df['next_service'] >= today) &
                          (df['next_service'] <= today + timedelta(days=30))].sort_values('next_service')
            if not soon_df.empty:
                for _, row in soon_df.iterrows():
                    days_left = (row['next_service'] - today).days
                    st.markdown(f"""
                    <div class="alert-card due-soon">
                        <div style="font-size:22px">🟡</div>
                        <div>
                            <p class="alert-title">{row['name']} — {row['phone']}</p>
                            <p class="alert-sub">📱 Model: {row['model'] or 'N/A'} &nbsp;|&nbsp; 
                               🗓️ Due: {row['next_service']} &nbsp;|&nbsp; 
                               ⏳ <b>{days_left} days remaining</b></p>
                        </div>
                    </div>""", unsafe_allow_html=True)
            else:
                st.success("✅ Nothing due in the next 30 days!")

        with tab3:
            exp_df = df[df['contract_end'] <= today + timedelta(days=60)].sort_values('contract_end')
            if not exp_df.empty:
                for _, row in exp_df.iterrows():
                    days_left = (row['contract_end'] - today).days
                    badge = "EXPIRED" if days_left < 0 else f"{days_left}d left"
                    st.markdown(f"""
                    <div class="alert-card expiring">
                        <div style="font-size:22px">📋</div>
                        <div>
                            <p class="alert-title">{row['name']} — {row['phone']}</p>
                            <p class="alert-sub">📱 Model: {row['model'] or 'N/A'} &nbsp;|&nbsp;
                               🗓️ Ends: {row['contract_end']} &nbsp;|&nbsp;
                               🔔 <b>{badge}</b></p>
                        </div>
                    </div>""", unsafe_allow_html=True)
            else:
                st.success("✅ No contracts expiring in 60 days!")
    else:
        st.info("No customer data found.")

# ========================= ADD SERVICE RECORD =========================
elif menu == "🔧 Add Service Record":
    page_header("🔧", "Add Service Record", "Log a completed service visit")

    df = load_customers()
    if not df.empty:
        with st.form("service_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                cust_options = df['name'] + " — " + df['phone']
                selected = st.selectbox("Select Customer *", cust_options)
                cust_id = int(df[cust_options == selected]['id'].values[0])
                service_date = st.date_input("Service Date", datetime.today())
                service_type = st.selectbox("Service Type",
                    ["Regular Maintenance", "Filter Replacement", "UV Lamp Replacement",
                     "RO Membrane Service", "Emergency Repair", "Annual Service", "Installation"])
            with col2:
                technician = st.text_input("Technician Name", placeholder="e.g. Ramesh Kumar")
                cost = st.number_input("Service Cost (₹)", min_value=0.0, step=50.0)
                update_next = st.checkbox("Update Next Service Date", value=True)
                if update_next:
                    next_svc_date = st.date_input("Set Next Service Date",
                                                   datetime.today() + timedelta(days=180))

            svc_notes = st.text_area("Service Notes", placeholder="Parts replaced, issues found...")

            if st.form_submit_button("💾 Save Service Record", type="primary", use_container_width=True):
                conn.execute("""INSERT INTO service_records VALUES (NULL,?,?,?,?,?,?)""",
                             (cust_id, str(service_date), service_type, technician, cost, svc_notes))
                if update_next:
                    conn.execute("UPDATE customers SET last_service=?, next_service=? WHERE id=?",
                                 (str(service_date), str(next_svc_date), cust_id))
                conn.commit()
                st.success("✅ Service record saved!")

        st.markdown("---")
        st.markdown('<p class="section-title">📋 Recent Service History</p>', unsafe_allow_html=True)
        records = load_service_records()
        if not records.empty:
            st.dataframe(records[['customer_name','service_date','service_type','technician','cost','notes']],
                         use_container_width=True, hide_index=True,
                         column_config={"cost": st.column_config.NumberColumn("Cost (₹)", format="₹%.0f")})
    else:
        st.info("Add customers first before logging service records.")

# ========================= REPORTS =========================
elif menu == "📈 Reports & Analytics":
    page_header("📈", "Reports & Analytics", "Business intelligence at a glance")

    df = load_customers()
    if not df.empty:
        df['purchase_date'] = pd.to_datetime(df['purchase_date'], errors='coerce')
        df['month'] = df['purchase_date'].dt.to_period('M').astype(str)

        tab1, tab2, tab3 = st.tabs(["📊 Sales Trends", "💧 Model Analysis", "💰 Revenue"])

        with tab1:
            monthly = df.groupby('month').size().reset_index(name='Customers')
            fig = px.line(monthly, x='month', y='Customers',
                          markers=True, title="Monthly Customer Acquisitions",
                          color_discrete_sequence=['#1565c0'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              xaxis=dict(showgrid=False), yaxis=dict(gridcolor='rgba(0,0,0,0.05)'))
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            model_counts = df['model'].value_counts().reset_index()
            model_counts.columns = ['Model', 'Count']
            fig2 = px.bar(model_counts, x='Count', y='Model', orientation='h',
                          color='Count', color_continuous_scale='Blues',
                          title="Purifier Models Installed")
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                               yaxis=dict(showgrid=False), xaxis=dict(gridcolor='rgba(0,0,0,0.05)'),
                               coloraxis_showscale=False)
            st.plotly_chart(fig2, use_container_width=True)

        with tab3:
            records = load_service_records()
            if not records.empty and 'cost' in records.columns:
                records['service_date'] = pd.to_datetime(records['service_date'], errors='coerce')
                records['month'] = records['service_date'].dt.to_period('M').astype(str)
                rev = records.groupby('month')['cost'].sum().reset_index()
                rev.columns = ['Month', 'Revenue']
                fig3 = px.bar(rev, x='Month', y='Revenue',
                              color='Revenue', color_continuous_scale='Blues',
                              title="Monthly Service Revenue (₹)")
                fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                   coloraxis_showscale=False)
                st.plotly_chart(fig3, use_container_width=True)
                col1, col2 = st.columns(2)
                col1.metric("Total Service Revenue", f"₹{records['cost'].sum():,.0f}")
                col2.metric("Avg Service Cost", f"₹{records['cost'].mean():,.0f}")
            else:
                st.info("No service records yet. Add service records to see revenue analytics.")
    else:
        st.info("No data available. Add customers to view reports.")

# ========================= EXPORT =========================
elif menu == "📥 Export & Backup":
    page_header("📥", "Export & Backup", "Download your data and manage company branding")

    df = load_customers()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">📤 Export Data</p>', unsafe_allow_html=True)
        if not df.empty:
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download Customers CSV", csv_data,
                               "veer_customers_backup.csv", "text/csv",
                               use_container_width=True)
            records = load_service_records()
            if not records.empty:
                svc_csv = records.to_csv(index=False).encode('utf-8')
                st.download_button("⬇️ Download Service Records CSV", svc_csv,
                                   "veer_service_records.csv", "text/csv",
                                   use_container_width=True)
            st.markdown(f"<p style='color:#546e7a;font-size:13px;margin-top:12px'>📦 {len(df)} customer records ready for export</p>", unsafe_allow_html=True)
        else:
            st.info("No data to export yet.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">🎨 Company Branding</p>', unsafe_allow_html=True)
        logo_file = st.file_uploader("Upload Company Logo (PNG/JPG)", type=['png', 'jpg', 'jpeg'])
        if logo_file:
            with open("logo.png", "wb") as f:
                f.write(logo_file.getbuffer())
            st.success("✅ Logo uploaded! Refresh to see it in the sidebar.")
            st.image(logo_file, width=120)
        elif os.path.exists("logo.png"):
            st.image("logo.png", width=120, caption="Current Logo")
            if st.button("🗑️ Remove Logo"):
                os.remove("logo.png")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ========================= SETTINGS =========================
elif menu == "⚙️ Settings":
    page_header("⚙️", "Settings", "Configure your system preferences")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">🏢 Business Information</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Business Name", value="Veer Sales and Services")
        st.text_input("Owner Name",    placeholder="Your name")
        st.text_input("Phone",         placeholder="+91 XXXXX XXXXX")
    with col2:
        st.text_input("Email",    placeholder="email@example.com")
        st.text_input("City",     placeholder="City, State")
        st.text_input("GST No.",  placeholder="GST Number (optional)")
    st.text_area("Address", placeholder="Full business address")
    if st.button("💾 Save Settings", type="primary"):
        st.success("✅ Settings saved!")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">🗄️ Database Management</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        df_count = load_customers()
        st.metric("Total Records", len(df_count))
    with col2:
        db_size = os.path.getsize("water_purifier.db") / 1024 if os.path.exists("water_purifier.db") else 0
        st.metric("Database Size", f"{db_size:.1f} KB")
    st.markdown('</div>', unsafe_allow_html=True)
