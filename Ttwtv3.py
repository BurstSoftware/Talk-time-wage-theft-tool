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
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    .win { color: #22c55e; }
    .loss { color: #ef4444; }
</style>
""", unsafe_allow_html=True)

# ====================== CONSTANTS ======================
NATE_PAY = 19.00
DAVID_PAY = OMAR_PAY = DYLAN_PAY = 22.50

# Historical productivity (pick + stow combined)
DAVID_UNITS_HR = 16.77
OMAR_UNITS_HR = 1.38
DYLAN_UNITS_HR = 16.77

# Nathan’s updated total units processed = 1814
NATE_TOTAL_UNITS = 1814
NATE_HISTORICAL_HOURS = 30.29
NATE_COMBINED_HR = NATE_TOTAL_UNITS / NATE_HISTORICAL_HOURS  # ≈ 59.92 units/hr combined

# Other Nathan rates
NATE_PICK_HR = 107.0
NATE_STOW_HR = 59.5
NATE_PACK_HR = 112.34

# ====================== SIDEBAR ======================
with st.sidebar:
    st.title("⚔️ Competitive Comparator")
    st.markdown("**Comparison Period**")
    hours = st.slider("Hours to compare", 1.0, 40.0, 10.0, 0.5)
    
    st.divider()
    st.markdown("**Nathan Rates (Editable)**")
    nate_pick = st.number_input("Nathan Pick Rate (units/hr)", value=NATE_PICK_HR, step=1.0)
    nate_stow = st.number_input("Nathan Stow Rate (units/hr)", value=NATE_STOW_HR, step=0.5)
    nate_pack = st.number_input("Nathan Pack Rate (units/hr)", value=NATE_PACK_HR, step=0.5)
    nate_combined = nate_pick + nate_stow

# ====================== HEADER ======================
st.markdown('<h1 class="main-header">Competitive Profitability & Loss Comparator</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">David vs Nathan • Omar vs Nathan • Team vs Nathan • Nathan Total Units: 1,814</p>', unsafe_allow_html=True)
st.divider()

# ====================== HELPER FUNCTION ======================
def calc_metrics(name: str, pay: float, units_hr: float, comparison_hours: float, nate_units_hr: float, nate_pay: float):
    units_produced = units_hr * comparison_hours
    labor_cost = pay * comparison_hours
    cost_per_unit = labor_cost / units_produced if units_produced > 0 else float('inf')
    
    nate_units = nate_units_hr * comparison_hours
    nate_labor_cost = nate_pay * comparison_hours
    
    units_delta = nate_units - units_produced
    cost_delta = labor_cost - nate_labor_cost
    
    units_per_dollar = units_produced / labor_cost if labor_cost > 0 else 0
    nate_units_per_dollar = nate_units_hr / nate_pay
    
    productivity_ratio = (nate_units_hr / units_hr) if units_hr > 0 else float('inf')
    
    return {
        "Name": name,
        "Pay/Hr": f"${pay:.2f}",
        "Units/Hr": round(units_hr, 2),
        "Units Produced": round(units_produced, 1),
        "Labor Cost": f"${labor_cost:.2f}",
        "Cost/Unit": f"${cost_per_unit:.4f}" if cost_per_unit != float('inf') else "∞",
        "Units/$": round(units_per_dollar, 3),
        "Nathan Units": round(nate_units, 1),
        "Units Lost vs Nathan": round(units_delta, 1),
        "Extra Cost vs Nathan": f"${cost_delta:.2f}",
        "Productivity Ratio": f"{productivity_ratio:.1f}x",
        "Gap": "win" if units_per_dollar > nate_units_per_dollar else "loss"
    }

# ====================== CALCULATIONS ======================
comparison_hours = hours
nate_combined = nate_pick + nate_stow

david_metrics = calc_metrics("David", DAVID_PAY, DAVID_UNITS_HR, comparison_hours, nate_combined, NATE_PAY)
omar_metrics = calc_metrics("Omar", OMAR_PAY, OMAR_UNITS_HR, comparison_hours, nate_combined, NATE_PAY)
dylan_metrics = calc_metrics("Dylan", DYLAN_PAY, DYLAN_UNITS_HR, comparison_hours, nate_combined, NATE_PAY)

# Team
team_units_hr = DAVID_UNITS_HR + OMAR_UNITS_HR + DYLAN_UNITS_HR
team_pay_total = DAVID_PAY + OMAR_PAY + DYLAN_PAY
team_units = team_units_hr * comparison_hours
team_labor_cost = team_pay_total * comparison_hours

team_metrics = {
    "Name": "TEAM (David+Omar+Dylan)",
    "Pay/Hr": f"${team_pay_total:.2f}",
    "Units/Hr": round(team_units_hr, 2),
    "Units Produced": round(team_units, 1),
    "Labor Cost": f"${team_labor_cost:.2f}",
    "Cost/Unit": f"${team_labor_cost / team_units:.4f}",
    "Units/$": round(team_units / team_labor_cost, 3),
    "Nathan Units": round(nate_combined * comparison_hours * 3, 1),
    "Units Lost vs Nathan": round(nate_combined * comparison_hours * 3 - team_units, 1),
    "Extra Cost vs Nathan": f"${team_labor_cost - (NATE_PAY * comparison_hours * 3):.2f}",
    "Productivity Ratio": f"{(nate_combined * 3) / team_units_hr:.1f}x",
    "Gap": "loss"
}

nate_baseline = {
    "Name": "Nathan (baseline)",
    "Pay/Hr": f"${NATE_PAY:.2f}",
    "Units/Hr": round(nate_combined, 2),
    "Units Produced": round(nate_combined * comparison_hours, 1),
    "Labor Cost": f"${NATE_PAY * comparison_hours:.2f}",
    "Cost/Unit": f"${NATE_PAY / nate_combined:.4f}",
    "Units/$": round(nate_combined / NATE_PAY, 3),
    "Nathan Units": round(nate_combined * comparison_hours, 1),
    "Units Lost vs Nathan": 0.0,
    "Extra Cost vs Nathan": "$0.00",
    "Productivity Ratio": "1.0x",
    "Gap": "baseline"
}

# ====================== TABS ======================
tab1, tab2, tab3 = st.tabs([
    "👥 Individual vs Nathan",
    "🏢 Team vs Nathan",
    "📊 Altair Visual Dashboard"
])

# TAB 1: Individual
with tab1:
    st.subheader("David vs Nathan")
    c1, c2 = st.columns([1, 1.4])
    with c1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("David Units", f"{david_metrics['Units Produced']}", f"-{david_metrics['Units Lost vs Nathan']} vs Nathan")
        st.metric("Labor Cost", david_metrics["Labor Cost"], david_metrics["Extra Cost vs Nathan"])
        st.metric("Cost per Unit", david_metrics["Cost/Unit"])
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        df_bar = pd.DataFrame({
            "Person": ["David", "Nathan"],
            "Units/Hr": [DAVID_UNITS_HR, nate_combined]
        })
        chart = alt.Chart(df_bar).mark_bar().encode(
            x=alt.X("Person:N", sort=None),
            y=alt.Y("Units/Hr:Q", title="Units per Hour"),
            color=alt.Color("Person:N", scale=alt.Scale(domain=["David", "Nathan"], range=["#ef4444", "#22c55e"]))
        ).properties(height=300, title="Units per Hour: David vs Nathan")
        st.altair_chart(chart, use_container_width=True)

    st.subheader("Omar vs Nathan")
    c3, c4 = st.columns([1, 1.4])
    with c3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Omar Units", f"{omar_metrics['Units Produced']}", f"-{omar_metrics['Units Lost vs Nathan']} vs Nathan")
        st.metric("Labor Cost", omar_metrics["Labor Cost"], omar_metrics["Extra Cost vs Nathan"])
        st.metric("Cost per Unit", omar_metrics["Cost/Unit"])
        st.markdown('</div>', unsafe_allow_html=True)
    with c4:
        df_omar = pd.DataFrame({
            "Person": ["Omar", "Nathan"],
            "Units/Hr": [OMAR_UNITS_HR, nate_combined]
        })
        chart_omar = alt.Chart(df_omar).mark_bar().encode(
            x=alt.X("Person:N"),
            y=alt.Y("Units/Hr:Q"),
            color=alt.Color("Person:N", scale=alt.Scale(domain=["Omar", "Nathan"], range=["#ef4444", "#22c55e"]))
        ).properties(height=300, title="Units per Hour: Omar vs Nathan")
        st.altair_chart(chart_omar, use_container_width=True)

# TAB 2: Team
with tab2:
    st.subheader("Full Team vs Nathan")
    col_t1, col_t2 = st.columns([1, 1])
    with col_t1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Team Units Produced", f"{team_metrics['Units Produced']}", f"-{team_metrics['Units Lost vs Nathan']} vs Nathan")
        st.metric("Team Labor Cost", team_metrics["Labor Cost"], team_metrics["Extra Cost vs Nathan"])
        st.metric("Team Cost/Unit", team_metrics["Cost/Unit"])
        st.markdown('</div>', unsafe_allow_html=True)
    with col_t2:
        st.metric("Team Productivity vs Nathan", team_metrics["Productivity Ratio"], "slower")
        st.caption(f"In {comparison_hours} hours the team produces **{team_metrics['Units Produced']}** units while 3× Nathan would produce **{nate_combined * comparison_hours * 3:,.0f}** units.")

    st.divider()
    st.subheader("Nathan Packing Advantage")
    st.metric("Potential Packed Units (Nathan Rate)", f"{round(nate_pack * comparison_hours):,}", "Team: 0 during talk time")

# TAB 3: Altair Dashboard
with tab3:
    st.subheader("Profitability Overview (Altair Charts)")

    all_data = [nate_baseline, david_metrics, omar_metrics, dylan_metrics, team_metrics]
    df = pd.DataFrame(all_data)

    # Units per Dollar Bar Chart
    bar_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("Name:N", sort=None, title=""),
        y=alt.Y("Units/$:Q", title="Units per Labor Dollar"),
        color=alt.Color("Name:N", scale=alt.Scale(
            domain=["Nathan (baseline)", "David", "Omar", "Dylan", "TEAM (David+Omar+Dylan)"],
            range=["#22c55e", "#ef4444", "#ef4444", "#ef4444", "#f59e0b"]
        )),
        tooltip=["Name", "Units/$", "Units Produced", "Labor Cost"]
    ).properties(
        height=420,
        title="Profitability: Units Produced per Dollar Spent"
    )

    st.altair_chart(bar_chart, use_container_width=True)

    st.dataframe(
        df[["Name", "Units/Hr", "Units Produced", "Labor Cost", "Cost/Unit", "Units Lost vs Nathan", "Extra Cost vs Nathan", "Productivity Ratio"]],
        use_container_width=True,
        hide_index=True
    )

# ====================== FOOTER ======================
st.caption(f"""
**Nathan Total Units Processed**: {NATE_TOTAL_UNITS} units over 30.29 hours  
Pick rate: {nate_pick} | Stow rate: {nate_stow} | Combined: {nate_combined:.2f} units/hr  
All rates are adjustable in the sidebar.
""")
st.success("✅ App updated with Altair charts • Nathan total units = 1,814")
