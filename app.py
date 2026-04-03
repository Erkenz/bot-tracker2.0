import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIG ---
st.set_page_config(
    page_title="Trader Pro", 
    page_icon="📈", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- THEME: MODERN BOLD & SOFT UI ---
st.markdown("""
    <style>
    /* 1. Global Reset */
    .stApp {
        background: #F4F7FB !important;
    }

    /* 2. Typography & Colors */
    h1, h2, h3, p, span, label, .stMarkdown {
        color: #1E293B !important;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    /* 3. The "Hero" Card (Total Balance) */
    div[data-testid="stMetric"] {
        background: #FFFFFF !important;
        border-radius: 24px !important;
        padding: 20px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.03) !important;
        border: 1px solid rgba(226, 232, 240, 0.8) !important;
    }
    
    /* Metric Labels (Blue Accent) */
    [data-testid="stMetricLabel"] > div {
        color: #3B82F6 !important; /* Electric Blue */
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 11px !important;
    }
    
    [data-testid="stMetricValue"] > div {
        color: #0F172A !important;
        font-weight: 800 !important;
        font-size: 32px !important;
    }

    /* 4. Inputs & Buttons (Modern Accent) */
    div[data-testid="stExpander"] {
        background: #FFFFFF !important;
        border-radius: 20px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02) !important;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 700 !important;
        border-radius: 14px !important;
        padding: 12px !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }

    /* 5. Tables & Tabs (Clean White) */
    .stDataFrame, .stTabs [data-baseweb="tab-list"] {
        background: #FFFFFF !important;
        border-radius: 16px !important;
        border: 1px solid #E2E8F0 !important;
    }
    
    /* Mobile Layout Fix */
    .block-container {
        max-width: 500px !important;
        padding-top: 2rem !important;
    }
    
    /* Status Dots */
    .dot { height: 10px; width: 10px; border-radius: 50%; display: inline-block; margin-right: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
    <div style="margin-bottom: 30px;">
        <h1 style="font-size: 32px; letter-spacing: -1px;">Hello Trader! 🚀</h1>
        <p style="color: #64748B !important; font-size: 16px;">Track your daily progress and hit your goals.</p>
    </div>
    """, unsafe_allow_html=True)

# --- DATA CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1f4yGEAE7WZRSl2RP9IqSLy0iYPw7PhMyjXjFS7cjcdE/edit?usp=sharing"

def get_data():
    df = conn.read(spreadsheet=SHEET_URL, ttl=2)
    df = df.dropna(how="all")
    if not df.empty:
        df.columns = df.columns.str.strip()
        df['Winst'] = pd.to_numeric(df['Winst'], errors='coerce')
        df['Datum'] = pd.to_datetime(df['Datum'], format='mixed')
        df = df.sort_values('Datum')
        df['Cumulatief'] = df['Winst'].cumsum()
    return df

df = get_data()

# --- INPUT SECTION ---
with st.expander("➕ Log Today's Result"):
    d_in = st.date_input("Select Date", value=datetime.now())
    a_in = st.number_input("Amount (€)", step=1.0)
    if st.button("Save to Cloud"):
        new_entry = pd.DataFrame([{"Datum": str(d_in), "Winst": a_in}])
        # Clean current data before concat
        clean_df = df.drop(columns=['Cumulatief'], errors='ignore') if not df.empty else df
        updated = pd.concat([clean_df, new_entry], ignore_index=True)
        conn.update(spreadsheet=SHEET_URL, data=updated)
        st.balloons()
        st.rerun()

st.write("")

# --- KEY METRICS ---
if not df.empty:
    st.markdown("### <span style='font-size:18px;'>Overview</span>", unsafe_allow_html=True)
    
    total = df['Winst'].sum()
    st.metric(label="Net Profit", value=f"€ {total:,.2f}")
    
    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        st.metric(label="Total Days", value=len(df))
        st.metric(label="Best Day", value=f"€ {df['Winst'].max():.0f}")
    with c2:
        st.metric(label="Avg / Day", value=f"€ {df['Winst'].mean():.2f}")
        st.metric(label="Drawdown (Max Loss)", value=f"€ {df['Winst'].min():.0f}")

    # PERFORMANCE GRAPH (High Contrast)
    st.write("")
    st.markdown("### Performance Curve")
    fig = go.Figure(go.Scatter(
        x=df['Datum'], y=df['Cumulatief'], 
        mode='lines+text', 
        line=dict(color='#3B82F6', width=5, shape='spline'), 
        fill='tozeroy', 
        fillcolor='rgba(59, 130, 246, 0.08)',
        text=[f"€{x:.0f}" for x in df['Cumulatief']],
        textfont=dict(color='#1E293B', size=11),
        textposition="top center"
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0), height=250, 
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
        xaxis=dict(showgrid=False, tickfont=dict(color='#94A3B8')), 
        yaxis=dict(showgrid=False, showticklabels=False, range=[df['Cumulatief'].min()*0.7, df['Cumulatief'].max()*1.4])
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # TABS (Daily & Weekly)
    st.write("")
    t1, t2 = st.tabs(["📅 Daily Logs", "📊 Weekly Stats"])
    with t1:
        # Color conditional formatting for the table
        d_df = df.sort_values('Datum', ascending=False).copy()
        d_df['Date'] = d_df['Datum'].dt.strftime('%d %b %Y')
        st.dataframe(d_df[['Date', 'Winst']].style.format({'Winst': '€ {:.2f}'}), use_container_width=True, hide_index=True)
        
    with t2:
        df['Week'] = df['Datum'].dt.isocalendar().week
        w_df = df.groupby('Week')['Winst'].sum().reset_index()
        st.dataframe(w_df.style.format({'Winst': '€ {:.2f}'}), use_container_width=True, hide_index=True)

else:
    st.info("Your dashboard is waiting for data. Log your first trade above!")
