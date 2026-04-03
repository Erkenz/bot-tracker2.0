import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIG ---
st.set_page_config(
    page_title="Trader Dashboard", 
    page_icon="💰", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- ULTRA MOBILE UX & SOFT UI STYLING ---
st.markdown("""
    <style>
    /* 1. Mobile App Lock: Voorkom horizontaal swipen en forceer witte achtergrond */
    html, body {
        max-width: 100vw;
        overflow-x: hidden;
        background-color: #F8F9FB;
    }

    /* 2. Container optimalisatie voor App-gevoel */
    .block-container { 
        padding-top: 1.5rem !important; 
        padding-bottom: 4rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 550px !important; 
    }

    /* 3. Typography */
    h1, h2, h3, p, span, label { 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
        color: #1A1A1A !important;
    }
    
    .main-header { margin-bottom: 25px; }
    .main-header h1 { font-size: 30px; font-weight: 800; margin-bottom: 0px; }
    .main-header p { font-size: 15px; color: #6E6E73 !important; }

    /* 4. Soft UI Metrics */
    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border-radius: 24px;
        padding: 18px !important;
        box-shadow: 6px 6px 12px rgba(163, 177, 198, 0.15), -6px -6px 12px rgba(255, 255, 255, 0.7);
        border: 1px solid #E5E7EB !important;
        width: 100% !important;
    }
    [data-testid="stMetricLabel"] { 
        color: #FF7A59 !important; 
        font-weight: 600 !important; 
        font-size: 12px !important;
        margin-bottom: 8px !important;
    }
    [data-testid="stMetricValue"] { font-size: 28px !important; font-weight: 700 !important; }

    /* 5. Tabellen & Tabs Styling (Clean White) */
    .stDataFrame, div[data-testid="stTable"], .stTabs {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 8px;
        border: 1px solid #E5E7EB;
    }
    
    /* 6. Expander & Add Trade Button */
    div[data-testid="stExpander"] {
        border: 1px solid #E5E7EB !important;
        border-radius: 20px !important;
        background-color: #FFFFFF !important;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.02);
    }
    .stButton>button {
        background-color: #FF7A59 !important;
        color: white !important;
        border-radius: 14px !important;
        border: none !important;
        width: 100%;
        font-weight: 700;
        padding: 12px;
        box-shadow: 0 4px 12px rgba(255, 122, 89, 0.2);
    }

    .status-dot {
        height: 7px; width: 7px; border-radius: 50%;
        display: inline-block; margin-right: 6px;
    }

    /* Verberg Streamlit menu/footer voor cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="main-header"><h1>Hello Trader!</h1><p>Let’s grow your portfolio.</p></div>', unsafe_allow_html=True)

# --- DATA CONNECTIE ---
conn = st.connection("gsheets", type=GSheetsConnection)
# JOUW LINK IS HIER VERWERKT:
SHEET_URL = "https://docs.google.com/spreadsheets/d/1f4yGEAE7WZRSl2RP9IqSLy0iYPw7PhMyjXjFS7cjcdE/edit?usp=sharing"

def get_data():
    df = conn.read(spreadsheet=SHEET_URL, ttl=2)
    df = df.dropna(how="all")
    if not df.empty:
        df.columns = df.columns.str.strip()
        df['Winst'] = pd.to_numeric(df['Winst'], errors='coerce')
        # Flexibele datum parsing
        df['Datum'] = pd.to_datetime(df['Datum'], format='mixed')
        df = df.sort_values('Datum')
        df['Cumulatief'] = df['Winst'].cumsum()
    return df

try:
    df = get_data()
except Exception as e:
    st.error("Data kon niet worden geladen. Check je Google Sheet of Secrets.")
    df = pd.DataFrame()

# --- ADD TRADE ---
with st.expander("➕ Add Trade", expanded=False):
    datum_input = st.date_input("Datum", value=datetime.now())
    bedrag_input = st.number_input("Bedrag (€)", step=1.0, format="%.2f")
    if st.button("Save Transaction"):
        new_row = pd.DataFrame([{"Datum": str(datum_input), "Winst": bedrag_input}])
        updated_df = pd.concat([df.drop(columns=['Cumulatief'], errors='ignore') if not df.empty else df, new_row], ignore_index=True)
        conn.update(spreadsheet=SHEET_URL, data=updated_df)
        st.success("Saved!")
        st.rerun()

st.write("")

# --- DASHBOARD ---
if not df.empty:
    st.markdown("### Key Metrics")
    
    # Total Balance Card (Full Width)
    total_val = df['Winst'].sum()
    st.metric(label="Total Balance", value=f"€ {total_val:,.2f}")
    
    st.write("")
    
    # Grid van 2x2 kleine metrics
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div><span class="status-dot" style="background-color:#FF7A59;"></span><span style="font-size:12px; font-weight:600; color:#FF7A59;">Total Days</span></div>', unsafe_allow_html=True)
        st.metric(label="", value=len(df))
        st.markdown('<div style="margin-bottom:15px"></div>', unsafe_allow_html=True)
        st.markdown('<div><span class="status-dot" style="background-color:#34C759;"></span><span style="font-size:12px; font-weight:600; color:#34C759;">Best Day</span></div>', unsafe_allow_html=True)
        st.metric(label="", value=f"€{df['Winst'].max():.0f}")
        
    with c2:
        st.markdown('<div><span class="status-dot" style="background-color:#FFCC00;"></span><span style="font-size:12px; font-weight:600; color:#FFCC00;">Avg / Day</span></div>', unsafe_allow_html=True)
        st.metric(label="", value=f"€{df['Winst'].mean():.2f}")
        st.markdown('<div style="margin-bottom:15px"></div>', unsafe_allow_html=True)
        st.markdown('<div><span class="status-dot" style="background-color:#FF3B30;"></span><span style="font-size:12px; font-weight:600; color:#FF3B30;">Worst Day</span></div>', unsafe_allow_html=True)
        st.metric(label="", value=f"€{df['Winst'].min():.0f}")

    # --- PERFORMANCE GRAPH ---
    st.write("")
    st.markdown("### Performance Curve")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Datum'], y=df['Cumulatief'], 
        mode='lines+text', 
        line=dict(color='#FF7A59', width=4, shape='spline'), 
        fill='tozeroy', 
        fillcolor='rgba(255, 122, 89, 0.05)',
        text=[f"€{x:.0f}" for x in df['Cumulatief']],
        textposition="top center",
        textfont=dict(size=10, color='#1A1A1A')
    ))
    
    fig.update_layout(
        margin=dict(l=5, r=5, t=35, b=0), height=220, 
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
        xaxis=dict(showgrid=False, tickfont=dict(color='#86868B', size=10)), 
        yaxis=dict(showgrid=False, showticklabels=False, range=[df['Cumulatief'].min()*0.7, df['Cumulatief'].max()*1.4])
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # --- TABLES (TABS) ---
    st.write("")
    tab1, tab2 = st.tabs(["📅 Daily Logs", "📊 Weekly Stats"])
    
    with tab1:
        daily_df = df.sort_values('Datum', ascending=False).copy()
        daily_df['Date'] = daily_df['Datum'].dt.strftime('%a, %d %b')
        st.dataframe(daily_df[['Date', 'Winst']].rename(columns={'Winst': 'Amount (€)'}), use_container_width=True, hide_index=True)
        
    with tab2:
        df['Week'] = df['Datum'].dt.isocalendar().week
        weekly = df.groupby('Week')['Winst'].sum().reset_index()
        st.dataframe(weekly.rename(columns={'Week': 'Week #', 'Winst': 'Profit (€)'}), use_container_width=True, hide_index=True)

else:
    st.info("No data yet. Start by adding your first trade!")
