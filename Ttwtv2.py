import streamlit as st
import pandas as pd
import altair as alt

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="Competitive Profitability & Loss Comparator",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header { font-size: 2.8rem; font-weight: 700; margin-bottom: 0.2rem; }
    .sub-header { color: #94a3b8; font-size: 1.15rem; }
    .metric-card {
        background: linear-gradient(135deg, #0f172a, #1e2937);
        padding: 1.75rem;
        border-radius: 16px;
        border: 1px solid #334155;
    }
    .win { color: #22c55e; }
    .loss { color: #ef4444; }
</style>
""", unsafe_allow_html=True)

# ====================== CONSTANTS ======================
NATE_PAY = 19.00
DAVID_PAY = OMAR_PAY = DYLAN_PAY = 22.50

DAVID_UNITS_HR = 16.77
OMAR_UNITS_HR = 1.38
DYLAN_UNITS_HR = 16.77

NATE_PICK_HR = 107.0
NATE_STOW_HR = 59.5
NATE_COMBINED_HR = NATE_PICK_HR + NATE_STOW_HR  # 166.5
NATE_PACK_HR = 112.34

# ====================== SIDEBAR ======================
with st.sidebar:
    st.title("⚔️ Altair Comparison Tool")
    hours = st.slider("Comparison Hours", 1.0, 40.0, 10.0, 0.5)
    
    st.divider()
    st.markdown("**Nathan Rates (editable)**")
    nate_pick = st.number_input("Nathan Pick Rate", value=NATE_PICK_HR, step=1.0)
    nate_stow = st.number_input("Nathan Stow Rate", value=NATE_STOW_HR, step=0.5)
    nate_pack = st.number_input("Nathan Pack Rate", value=NATE_PACK_HR, step=0.5)
    nate_combined = nate_pick + nate_stow

# ====================== HEADER ======================
st.markdown('<h1 class="main-header">Competitive Profitability & Loss Comparator</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">David vs Nathan • Omar vs Nathan • Full Team vs Nathan (Altair Charts)</p>', unsafe_allow_html=True)
st.divider()

# ====================== HELPER FUNCTION ======================
def calc_metrics(name, pay, units_hr, hours, nate_units_hr, nate_pay):
    units = units_hr * hours
    cost = pay * hours
    cost_per_unit = cost / units if units > 0 else float('inf')
    nate_units = nate_units_hr * hours
    nate_cost = nate_pay * hours
    
    return {
        "Name": name,
        "Pay/Hr": f"${pay:.2f}",
        "Units/Hr": round(units_hr, 2),
        "Units Produced": round(units, 1),
        "Labor Cost": f"${cost:.2f}",
        "Cost/Unit": f"${cost_per_unit:.4f}" if cost_per_unit != float('inf') else "∞",
        "Units/$": round(units / cost, 3) if cost > 0 else 0,
        "Nathan Units": round(nate_units, 1),
        "Units Lost vs Nathan": round(nate_units - units, 1),
        "Extra Cost vs Nathan": f"${cost - nate_cost:.2f}",
        "Productivity vs Nathan": f"{(nate_units_hr / units_hr):.1f}x" if units_hr > 0 else "∞"
    }

# ====================== CALCULATIONS ======================
david = calc_metrics("David", DAVID_PAY, DAVID_UNITS_HR, hours, nate_combined, NATE_PAY)
omar = calc_metrics("Omar", OMAR_PAY, OMAR_UNITS_HR, hours, nate_combined, NATE_PAY)
dylan = calc_metrics("Dylan", DYLAN_PAY, DYLAN_UNITS_HR, hours, nate_combined, NATE_PAY)

team_units_hr = DAVID_UNITS_HR + OMAR_UNITS_HR + DYLAN_UNITS_HR
team_pay = DAVID_PAY + OMAR_PAY + DYLAN_PAY
team_units = team_units_hr * hours
team_cost = team_pay * hours
team_nate_equiv = nate_combined * hours * 3

team_metrics = {
    "Name": "TEAM (David+Omar+Dylan)",
    "Pay/Hr": f"${team_pay:.2f}",
    "Units/Hr": round(team_units_hr, 2),
    "Units Produced": round(team_units, 1),
    "Labor Cost": f"${team_cost:.2f}",
    "Cost/Unit": f"${team_cost / team_units:.4f}",
    "Units/$": round(team_units / team_cost, 3),
    "Nathan Units": round(team_nate_equiv, 1),
    "Units Lost vs Nathan": round(team_nate_equiv - team_units, 1),
    "Extra Cost vs Nathan": f"${team_cost - (NATE_PAY * hours * 3):.2f}",
    "Productivity vs Nathan": f"{(nate_combined * 3 / team_units_hr):.1f}x"
}

nate_baseline = {
    "Name": "Nathan (Baseline)",
    "Pay/Hr": f"${NATE_PAY:.2f}",
    "Units/Hr": round(nate_combined, 2),
    "Units Produced": round(nate_combined * hours, 1),
    "Labor Cost": f"${NATE_PAY * hours:.2f}",
    "Cost/Unit": f"${NATE_PAY / nate_combined:.4f}",
    "Units/$": round(nate_combined / NATE_PAY, 3),
    "Nathan Units": round(nate_combined * hours, 1),
    "Units Lost vs Nathan": 0.0,
    "Extra Cost vs Nathan": "$0.00",
    "Productivity vs Nathan": "1.0x"
}

# ====================== TABS ======================
tab1, tab2, tab3 = st.tabs([
    "👥 Individual Comparisons",
    "🏢 Team vs Nathan",
    "📊 Altair Profitability Dashboard"
])

# TAB 1: Individual
with tab1:
    st.subheader("David vs Nathan")
    c1, c2 = st.columns([1, 1.8])
    with c1:
        st.metric("Units Produced", f"{david['Units Produced']}", f"-{david['Units Lost vs Nathan']} vs Nathan")
        st.metric("Labor Cost", david["Labor Cost"], david["Extra Cost vs Nathan"])
        st.metric("Cost per Unit", david["Cost/Unit"])
    with c2:
        df_d = pd.DataFrame([
            {"Person": "David", "Units/Hr": DAVID_UNITS_HR},
            {"Person": "Nathan", "Units/Hr": nate_combined}
        ])
        chart_d = alt.Chart(df_d).mark_bar().encode(
            x=alt.X('Person:N', sort=None),
            y=alt.Y('Units/Hr:Q', title='Units per Hour'),
            color=alt.Color('Person:N', scale=alt.Scale(domain=['David','Nathan'], range=['#ef4444','#22c55e']))
        ).properties(height=300, title="Units per Hour: David vs Nathan")
        st.altair_chart(chart_d, use_container_width=True)

    st.subheader("Omar vs Nathan")
    c3, c4 = st.columns([1, 1.8])
    with c3:
        st.metric("Units Produced", f"{omar['Units Produced']}", f"-{omar['Units Lost vs Nathan']} vs Nathan")
        st.metric("Labor Cost", omar["Labor Cost"], omar["Extra Cost vs Nathan"])
        st.metric("Cost per Unit", omar["Cost/Unit"])
    with c4:
        df_o = pd.DataFrame([
            {"Person": "Omar", "Units/Hr": OMAR_UNITS_HR},
            {"Person": "Nathan", "Units/Hr": nate_combined}
        ])
        chart_o = alt.Chart(df_o).mark_bar().encode(
            x='Person:N',
            y='Units/Hr:Q',
            color=alt.Color('Person:N', scale=alt.Scale(domain=['Omar','Nathan'], range=['#ef4444','#22c55e']))
        ).properties(height=300, title="Units per Hour: Omar vs Nathan")
        st.altair_chart(chart_o, use_container_width=True)

# TAB 2: Team
with tab2:
    st.subheader("Full Team vs Nathan")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.metric("Team Units Produced", f"{team_metrics['Units Produced']}", f"-{team_metrics['Units Lost vs Nathan']} vs Nathan")
        st.metric("Team Labor Cost", team_metrics["Labor Cost"], team_metrics["Extra Cost vs Nathan"])
    with col2:
        st.metric("Team Productivity", team_metrics["Productivity vs Nathan"], "slower than Nathan")
        st.metric("Pack Opportunity (Nathan Rate)", f"{round(nate_pack * hours):,} units", "Team = 0 during talk time")

# TAB 3: Altair Dashboard
with tab3:
    st.subheader("Profitability Overview (Altair)")
    
    all_data = [nate_baseline, david, omar, dylan, team_metrics]
    df_all = pd.DataFrame(all_data)
    
    st.dataframe(df_all, use_container_width=True, hide_index=True)
    
    # Altair Bar Chart - Units per Dollar
    chart_profit = alt.Chart(df_all).mark_bar().encode(
        x=alt.X('Name:N', sort=None, title=None),
        y=alt.Y('Units/$:Q', title='Units Produced per Labor Dollar'),
        color=alt.condition(
            alt.datum.Name == 'Nathan (Baseline)',
            alt.value('#22c55e'),
            alt.value('#ef4444')
        ),
        tooltip=['Name', 'Units/$', 'Units Produced', 'Labor Cost']
    ).properties(
        height=450,
        title="Units per Dollar – Profitability Comparison"
    ).configure_axis(labelFontSize=14, titleFontSize=15)
    
    st.altair_chart(chart_profit, use_container_width=True)
    
    st.success(f"**Key Insight**: In {hours} hours, the team loses **{team_metrics['Units Lost vs Nathan']:,.0f} units** and incurs **{team_metrics['Extra Cost vs Nathan']}** extra labor cost compared to Nathan-level performance.")

st.caption("""
Nathan historical: 30.29 hrs • 1,802 stow units • Pick avg 107/hr • Pack 112.34/hr  
All rates are pick + stow combined unless noted. Dylan uses David’s rate.
""")
