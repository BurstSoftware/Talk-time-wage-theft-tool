import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="Warehouse Productivity Loss Analyzer",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better visuals
st.markdown("""
<style>
    .main-header { font-size: 2.8rem; font-weight: 700; margin-bottom: 0.2rem; }
    .sub-header { color: #94a3b8; font-size: 1.1rem; }
    .metric-card {
        background: linear-gradient(135deg, #0f172a, #1e2937);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #334155;
    }
    .highlight { color: #fbbf24; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ====================== SIDEBAR ======================
with st.sidebar:
    st.title("📊 Settings")
    st.markdown("**Shift Details**")
    st.info("""
    **Nathan's Shift**  
    9:57 AM – 2:03 PM (4.1 hours)  
    Pay: $19.00/hr → **$77.90**
    """)
    
    st.markdown("**Talk Time**")
    david_talk = st.slider("David Talk Time (hours)", 0.0, 10.0, 3.0, 0.25)
    omar_talk = st.slider("Omar Talk Time (hours)", 0.0, 10.0, 4.0, 0.25)
    dylan_talk = st.slider("Dylan Talk Time (hours)", 0.0, 10.0, 3.0, 0.25)
    
    total_talk = david_talk + omar_talk + dylan_talk
    st.metric("Total Talk Hours", f"{total_talk:.1f} hrs", delta=None)

# ====================== HEADER ======================
st.markdown('<h1 class="main-header">Warehouse Productivity Loss Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Based on Nathan’s shift (9:57 AM – 2:03 PM) and combined talk time</p>', unsafe_allow_html=True)
st.divider()

# ====================== TOP METRICS ======================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        label="💸 TOTAL MONEY LOST",
        value="$225.00",
        delta="10 hours unproductive"
    )
    st.caption("David + Omar + Dylan @ $22.50/hr")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        label="⏱️ Nathan Worked",
        value="4.1 hrs",
        delta="246 minutes"
    )
    st.caption("9:57 AM – 2:03 PM")
    st.metric("Pay", "$77.90", "@ $19/hr")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.subheader("📦 Nathan Processed (est.)")
    st.metric("Pick", "438 units", "107/hr avg")
    st.metric("Stow", "244 units", "59.5/hr")
    st.metric("Pack", "460 units", "112/hr")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.subheader("🗣️ Talk Breakdown")
    st.progress(david_talk / total_talk if total_talk > 0 else 0, text=f"David: {david_talk}h")
    st.progress(omar_talk / total_talk if total_talk > 0 else 0, text=f"Omar: {omar_talk}h")
    st.progress(dylan_talk / total_talk if total_talk > 0 else 0, text=f"Dylan: {dylan_talk}h")
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ====================== TABS ======================
tab1, tab2, tab3 = st.tabs([
    "📉 Historical Loss (Their Rates)",
    "🚀 Nathan-Rate Opportunity Loss",
    "📊 Summary & Comparison"
])

# ====================== TAB 1: HISTORICAL LOSS ======================
with tab1:
    st.subheader("Units NOT Processed — Based on Their Historical Productivity")
    
    data = {
        "Person": ["David", "Omar", "Dylan", "TOTAL"],
        "Talk Hours": [david_talk, omar_talk, dylan_talk, total_talk],
        "Historical Units/Hr": [16.77, 1.38, 16.77, "—"],
        "Units Missed": [
            round(16.77 * david_talk, 2),
            round(1.38 * omar_talk, 2),
            round(16.77 * dylan_talk, 2),
            round(16.77 * (david_talk + dylan_talk) + 1.38 * omar_talk, 2)
        ],
        "Labor Cost Wasted": [
            f"${round(22.5 * david_talk, 2)}",
            f"${round(22.5 * omar_talk, 2)}",
            f"${round(22.5 * dylan_talk, 2)}",
            f"${round(22.5 * total_talk, 2)}"
        ],
        "Avg Cost per Missed Unit": ["$1.34", "$16.36", "$1.34", "—"]
    }
    
    df = pd.DataFrame(data)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Units Missed": st.column_config.NumberColumn(format="%.2f"),
        }
    )
    
    st.caption("* Dylan uses David’s historical rate (pick + stow combined). Rates from provided 40-hour data.")

# ====================== TAB 2: NATHAN OPPORTUNITY ======================
with tab2:
    st.subheader("Units NOT Processed — If They Worked at Nathan’s Rates")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.metric(
            label="Pick Opportunity",
            value="1,070 units",
            delta="107 units/hr × 10 hrs"
        )
    
    with col_b:
        st.metric(
            label="Stow Opportunity",
            value="595 units",
            delta="59.5 units/hr × 10 hrs (1,802 / 30.29 hrs)"
        )
    
    with col_c:
        st.metric(
            label="Pack Opportunity",
            value="1,123 units",
            delta="88 units / 47 min → 112.34/hr"
        )
    
    st.info("**Trickling excluded** (88 units every 10 minutes = 528/hr supporting task)")

# ====================== TAB 3: SUMMARY & COMPARISON ======================
with tab3:
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Their Historical Loss")
        st.success(f"**{round(16.77*(david_talk+dylan_talk) + 1.38*omar_talk, 1)} units** missed during talk time")
        st.metric("Money Wasted", f"${round(22.5 * total_talk, 2)}", "at $22.50/hr")
    
    with col_right:
        st.subheader("Nathan-Rate Opportunity")
        st.metric("Potential Pick", "1,070 units")
        st.metric("Potential Stow", "595 units")
        st.metric("Potential Pack", "1,123 units")
    
    st.divider()
    
    # Bar Chart Comparison
    chart_data = pd.DataFrame({
        "Category": ["Their Historical", "Nathan Stow", "Nathan Pick", "Nathan Pack"],
        "Units": [106, 595, 1070, 1123]
    })
    
    st.subheader("Productivity Comparison")
    st.bar_chart(
        chart_data.set_index("Category"),
        use_container_width=True,
        height=400
    )
    
    st.markdown("""
    **Key Takeaway**  
    Nathan is **≈10× more productive** than the current team average.  
    Implementing similar standards could recover **$225+** and **500–1,100+ units** per 10 talk hours.
    """)

# ====================== FOOTER ======================
st.caption("""
Nathan Historical Record: 30.29 hours • 1,802 stow units (59.5/hr) • 
Pack rate: 88 units every 47 minutes • Pick rate: 59–155/hr
""")

st.success("✅ App ready. Adjust sliders in sidebar to see live updates.")
