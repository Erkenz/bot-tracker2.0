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

# --- THEME FIX & SOFT UI STYLING ---
st.markdown("""
    <style>
    /* 1. FORCEER ACHTERGROND (Niet meer transparant) */
    .stApp {
        background-color: #F8F9FB !important;
    }

    /* 2. FORCEER TEKSTKLEUR (Overal donkergrijs/zwart) */
    html, body, [data-testid="stWidgetLabel"], h1, h2, h3, p, span, label, .stMarkdown {
        color: #1A1A1A !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* 3. VERBETERDE METRICS (Wit blok met schaduw) */
    [data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border-radius: 20px !important;
        padding: 15px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
        border: 1px solid #E5E7EB !important;
    }
    
    /* Metric Labels (Oranje) */
    [data-testid="stMetricLabel"] > div {
        color: #FF7A59 !important;
        font-weight: 700 !important;
    }
    
    /* Metric Waarden (Zwart) */
    [data-testid="stMetricValue"] > div {
        color: #1A1A1A !important;
        font-weight: 800 !important;
    }

    /* 4. TABELLEN FIX (Geen zwarte achtergrond meer) */
    .stDataFrame, div[data-testid="stTable"], .stTabs {
        background-color: #FFFFFF !important;
        border-radius: 15px !important;
        border: 1px solid #E5E7EB !important;
        color: #1A1A1A !important;
    }
    
    /* Tabel Headers tekstkleur */
    [data-testid="stHeader"] {
        background-color: #F8F9FB !important;
    }

    /* 5. INPUTS & BUTTONS */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border-radius: 15px !important;
        border: 1px solid #E5E7EB !important;
    }
    .stButton>button {
        background-color: #FF7A59 !important;
        color: white !important;
        border: none !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
    }

    /* 6. MOBILE FIXES */
    .block-container {
        max-width: 500px !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div><h1 style="margin-bottom:0px;">Hello Trader!</h1><p style="color:#6E6E73 !important;">Let’s grow your portfolio.</p></div>', unsafe_allow_html=True)

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
with st.expander("➕ Add Trade"):
    datum_in = st.date_input("Datum", value=datetime.now())
    bedrag_in = st.number_input("Bedrag (€)", step=1.0)
    if st.button("Save"):
        new_row = pd.DataFrame([{"Datum": str(datum_in), "Winst": bedrag_in}])
        # Filter de cumulatieve kolom weg voordat we concat doen
        current_data = df.drop(columns=['Cumulatief'], errors='ignore') if not df.empty else df
        updated_df = pd.concat([current_data, new_row], ignore_index=True)
        conn.update(spreadsheet=SHEET_URL, data=updated_df)
        st.success("Success!")
        st.rerun()

st.write("")

# --- DASHBOARD ---
if not df.empty:
    st.markdown("### Key Metrics")
    st.metric(label="Total Balance", value=f"€ {df['Winst'].sum():,.2f}")
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric(label="Total Days", value=len(df))
        st.metric(label="Max Day", value=f"€ {df['Winst'].max():.0f}")
    with c2:
        st.metric(label="Avg / Day", value=f"€ {df['Winst'].mean():.2f}")
        st.metric(label="Min Day", value=f"€ {df['Winst'].min():.0f}")

    # PERFORMANCE CHART
    st.write("")
    st.markdown("### Performance")
    fig = go.Figure(go.Scatter(
        x=df['Datum'], y=df['Cumulatief'], 
        mode='lines+text', 
        line=dict(color='#FF7A59', width=4, shape='spline'), 
        fill='tozeroy', 
        fillcolor='rgba(255, 122, 89, 0.05)',
        text=[f"€{x:.0f}" for x in df['Cumulatief']],
        textposition="top center"
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0), height=200, 
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
        xaxis=dict(showgrid=False, tickfont=dict(color='#86868B')), 
        yaxis=dict(showgrid=False, showticklabels=False, range=[df['Cumulatief'].min()*0.8, df['Cumulatief'].max()*1.3])
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # TABS
    st.write("")
    t1, t2 = st.tabs(["📅 Daily", "📊 Weekly"])
    with t1:
        d_df = df.sort_values('Datum', ascending=False).copy()
        d_df['Date'] = d_df['Datum'].dt.strftime('%a, %d %b')
        st.dataframe(d_df[['Date', 'Winst']], use_container_width=True, hide_index=True)
    with t2:
        df['Week'] = df['Datum'].dt.isocalendar().week
        w_df = df.groupby('Week')['Winst'].sum().reset_index()
        st.dataframe(w_df, use_container_width=True, hide_index=True)

else:
    st.info("Voeg je eerste data toe!")
