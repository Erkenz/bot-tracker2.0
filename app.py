import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Trader Dashboard", page_icon="💰", layout="centered")

# --- HYBRID MODERN UI STYLING ---
st.markdown("""
    <style>
    /* Achtergrond & Breedte */
    .stApp { background-color: #F8F9FB; }
    .block-container { 
        padding-top: 2rem !important; 
        max-width: 550px !important; 
    }

    /* Typografie */
    h1, h2, h3, p, span, label { 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
        color: #1A1A1A !important;
    }
    
    /* Header Styling */
    .main-header { margin-bottom: 25px; }
    .main-header h1 { font-size: 32px; font-weight: 800; margin-bottom: 0px; }
    .main-header p { font-size: 16px; color: #6E6E73 !important; }

    /* Key Metrics Kaarten */
    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border-radius: 24px;
        padding: 20px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        border: 1px solid #E5E7EB !important;
        text-align: left;
    }
    [data-testid="stMetricLabel"] { 
        color: #FF7A59 !important; 
        font-weight: 600 !important; 
        font-size: 13px !important;
        margin-bottom: 8px !important;
    }
    [data-testid="stMetricValue"] { font-size: 32px !important; font-weight: 700 !important; }

    /* Custom Tabel Styling (Gedwongen Wit) */
    .stDataFrame, div[data-testid="stTable"] {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 10px;
        border: 1px solid #E5E7EB;
    }
    
    /* Expander & Knoppen */
    div[data-testid="stExpander"] {
        border: 1px solid #E5E7EB !important;
        border-radius: 20px !important;
        background-color: #FFFFFF !important;
    }
    .stButton>button {
        background-color: #FF7A59 !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        width: 100%;
        font-weight: 700;
        padding: 12px;
        box-shadow: 0 4px 10px rgba(255, 122, 89, 0.2);
    }

    .status-dot {
        height: 8px; width: 8px; border-radius: 50%;
        display: inline-block; margin-right: 6px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="main-header"><h1>Hello Trader!</h1><p>Let’s grow your portfolio.</p></div>', unsafe_allow_html=True)

# --- DATA ---
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

# --- ADD TRADE ---
with st.expander("➕ Add Trade", expanded=False):
    c_in1, c_in2 = st.columns(2)
    with c_in1: datum = st.date_input("Datum")
    with c_in2: bedrag = st.number_input("Bedrag (€)", step=1.0)
    if st.button("Save Transaction"):
        new_row = pd.DataFrame([{"Datum": str(datum), "Winst": bedrag}])
        updated_df = pd.concat([df.drop(columns=['Cumulatief'], errors='ignore') if not df.empty else df, new_row], ignore_index=True)
        conn.update(spreadsheet=SHEET_URL, data=updated_df)
        st.success("Success!")
        st.rerun()

st.write("")

# --- DASHBOARD ---
if not df.empty:
    st.markdown("### Key Metrics")
    
    # 1. Big Balance Card
    total_val = 500 + df['Winst'].sum()
    st.metric(label="Total Balance", value=f"€ {total_val:,.2f}")
    
    st.write("")
    
    # 2. Grid Metrics (2x2)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div><span class="status-dot" style="background-color:#FF7A59;"></span><span style="font-size:12px; font-weight:600; color:#FF7A59;">Total Days</span></div>', unsafe_allow_html=True)
        st.metric(label="", value=len(df))
        
        st.write("")
        st.markdown('<div><span class="status-dot" style="background-color:#34C759;"></span><span style="font-size:12px; font-weight:600; color:#34C759;">Max Gain</span></div>', unsafe_allow_html=True)
        st.metric(label="", value=f"€ {df['Winst'].max():.2f}")
        
    with col2:
        st.markdown('<div><span class="status-dot" style="background-color:#FFCC00;"></span><span style="font-size:12px; font-weight:600; color:#FFCC00;">Avg / Day</span></div>', unsafe_allow_html=True)
        st.metric(label="", value=f"€ {df['Winst'].mean():.2f}")
        
        st.write("")
        st.markdown('<div><span class="status-dot" style="background-color:#FF3B30;"></span><span style="font-size:12px; font-weight:600; color:#FF3B30;">Max Loss</span></div>', unsafe_allow_html=True)
        st.metric(label="", value=f"€ {df['Winst'].min():.2f}")

    # 3. Performance Graph
    st.write("")
    st.markdown("### Performance Curve")
    fig = go.Figure(go.Scatter(
        x=df['Datum'], y=df['Cumulatief'], 
        mode='lines', 
        line=dict(color='#FF7A59', width=4, shape='spline'), 
        fill='tozeroy', 
        fillcolor='rgba(255, 122, 89, 0.05)'
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0), height=180, 
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
        xaxis=dict(showgrid=False, tickfont=dict(color='#86868B')), 
        yaxis=dict(showgrid=False, showticklabels=False)
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # 4. Tables (White Design)
    st.write("")
    tab1, tab2 = st.tabs(["📅 Daily Logs", "📊 Weekly Overview"])
    
    with tab1:
        daily_df = df.sort_values('Datum', ascending=False).copy()
        daily_df['Date'] = daily_df['Datum'].dt.strftime('%a, %d %b')
        st.dataframe(daily_df[['Date', 'Winst']].rename(columns={'Winst': 'Amount (€)'}), use_container_width=True, hide_index=True)
        
    with tab2:
        df['Week'] = df['Datum'].dt.isocalendar().week
        weekly = df.groupby('Week')['Winst'].sum().reset_index()
        st.dataframe(weekly.rename(columns={'Week': 'Week #', 'Winst': 'Profit (€)'}), use_container_width=True, hide_index=True)

else:
    st.info("Ready to grow? Add your first trade above!")