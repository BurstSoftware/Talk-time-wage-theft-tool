import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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

# ====================== CONSTANTS (from your data) ======================
NATE_PAY = 19.00
DAVID_PAY = 22.50
OMAR_PAY = 22.50
DYLAN_PAY = 22.50

# Historical productivity (pick + stow combined)
DAVID_UNITS_HR = 16.77
OMAR_UNITS_HR = 1.38
DYLAN_UNITS_HR = 16.77   # using David’s average as provided

# Nathan’s rates
NATE_PICK_HR = 107.0
NATE_STOW_HR = 59.5
NATE_COMBINED_HR = NATE_PICK_HR + NATE_STOW_HR   # 166.5
NATE_PACK_HR = 112.34
NATE_TRICKLE_HR = 528.0   # 88 units every 10 min (supporting task)

# Nathan’s historical record for reference
NATE_HISTORICAL_HOURS = 30.29
NATE_TOTAL_STOW = 1802
NATE_COST_PER_UNIT_HIST = 19.0 / NATE_COMBINED_HR

# ====================== SIDEBAR ======================
with st.sidebar:
    st.title("⚔️ Comparison Tool")
    st.markdown("**Comparison Period**")
    hours = st.slider("Hours to compare", 1.0, 40.0, 10.0, 0.5, help="Default = 10 hours of talk time")
    
    st.divider()
    st.markdown("**Editable Nathan Rates**")
    nate_pick = st.number_input("Nathan Pick Rate (units/hr)", value=NATE_PICK_HR, step=1.0)
    nate_stow = st.number_input("Nathan Stow Rate (units/hr)", value=NATE_STOW_HR, step=0.5)
    nate_pack = st.number_input("Nathan Pack Rate (units/hr)", value=NATE_PACK_HR, step=0.5)
    nate_combined = nate_pick + nate_stow
    
    st.divider()
    st.caption("Data sourced from your shift records and 40-hour historicals")

# ====================== HEADER ======================
st.markdown('<h1 class="main-header">Competitive Profitability & Loss Comparator</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">David vs Nathan • Omar vs Nathan • Team (David + Omar + Dylan) vs Nathan</p>', unsafe_allow_html=True)
st.divider()

# ====================== HELPER FUNCTION ======================
def calc_metrics(name: str, pay: float, units_hr: float, comparison_hours: float, nate_units_hr: float, nate_pay: float):
    units_produced = units_hr * comparison_hours
    labor_cost = pay * comparison_hours
    cost_per_unit = labor_cost / units_produced if units_produced > 0 else float('inf')
    
    nate_units = nate_units_hr * comparison_hours
    nate_labor_cost = nate_pay * comparison_hours
    
    units_delta = nate_units - units_produced
    cost_delta = labor_cost - nate_labor_cost   # extra cost paid vs Nathan doing it
    
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
        "Productivity Ratio (× Nathan)": f"{productivity_ratio:.1f}x" if productivity_ratio != float('inf') else "∞",
        "Profitability Gap": "win" if units_per_dollar > nate_units_per_dollar else "loss"
    }

# ====================== CALCULATIONS ======================
comparison_hours = hours

# Individual calculations (pick + stow)
david_metrics = calc_metrics("David", DAVID_PAY, DAVID_UNITS_HR, comparison_hours, nate_combined, NATE_PAY)
omar_metrics = calc_metrics("Omar", OMAR_PAY, OMAR_UNITS_HR, comparison_hours, nate_combined, NATE_PAY)
dylan_metrics = calc_metrics("Dylan", DYLAN_PAY, DYLAN_UNITS_HR, comparison_hours, nate_combined, NATE_PAY)

# Team
team_units_hr = DAVID_UNITS_HR + OMAR_UNITS_HR + DYLAN_UNITS_HR
team_pay_total = DAVID_PAY + OMAR_PAY + DYLAN_PAY
team_labor_cost = team_pay_total * comparison_hours
team_units = team_units_hr * comparison_hours

team_metrics = {
    "Name": "TEAM (David + Omar + Dylan)",
    "Pay/Hr": f"${team_pay_total:.2f} total",
    "Units/Hr": round(team_units_hr, 2),
    "Units Produced": round(team_units, 1),
    "Labor Cost": f"${team_labor_cost:.2f}",
    "Cost/Unit": f"${team_labor_cost / team_units:.4f}",
    "Units/$": round(team_units / team_labor_cost, 3),
    "Nathan Units": round(nate_combined * comparison_hours * 3, 1),  # if Nathan replaced all 3
    "Units Lost vs Nathan": round((nate_combined * comparison_hours * 3) - team_units, 1),
    "Extra Cost vs Nathan": f"${team_labor_cost - (NATE_PAY * comparison_hours * 3):.2f}",
    "Productivity Ratio (× Nathan)": f"{(nate_combined * 3) / team_units_hr:.1f}x",
    "Profitability Gap": "loss"
}

# Nathan baseline
nate_baseline = {
    "Name": "Nathan (baseline)",
    "Pay/Hr": f"${NATE_PAY:.2f}",
    "Units/Hr": round(nate_combined, 2),
    "Units Produced": round(nate_combined * comparison_hours, 1),
    "Labor Cost": f"${NATE_PAY * comparison_hours:.2f}",
    "Cost/Unit": f"${NATE_COST_PER_UNIT_HIST:.4f}",
    "Units/$": round(nate_combined / NATE_PAY, 3),
    "Nathan Units": round(nate_combined * comparison_hours, 1),
    "Units Lost vs Nathan": 0.0,
    "Extra Cost vs Nathan": "$0.00",
    "Productivity Ratio (× Nathan)": "1.0x",
    "Profitability Gap": "baseline"
}

# ====================== MAIN TABS ======================
tab1, tab2, tab3 = st.tabs([
    "👥 Individual vs Nathan",
    "🏢 Team vs Nathan",
    "📊 Visual Profitability Dashboard"
])

# TAB 1: Individual Comparisons
with tab1:
    st.subheader("David vs Nathan")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("David Units Produced", f"{david_metrics['Units Produced']} units", f"-{david_metrics['Units Lost vs Nathan']} vs Nathan")
        st.metric("David Labor Cost", david_metrics["Labor Cost"], f"{david_metrics['Extra Cost vs Nathan']} extra")
        st.metric("Cost per Unit", david_metrics["Cost/Unit"], f"vs Nathan ${NATE_COST_PER_UNIT_HIST:.4f}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_d2:
        fig_d = go.Figure()
        fig_d.add_trace(go.Bar(name="David", x=["Units/Hr"], y=[DAVID_UNITS_HR], marker_color="#ef4444"))
        fig_d.add_trace(go.Bar(name="Nathan", x=["Units/Hr"], y=[nate_combined], marker_color="#22c55e"))
        fig_d.update_layout(title="Units per Hour: David vs Nathan", barmode="group", height=280)
        st.plotly_chart(fig_d, use_container_width=True)
    
    st.subheader("Omar vs Nathan")
    col_o1, col_o2 = st.columns(2)
    with col_o1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Omar Units Produced", f"{omar_metrics['Units Produced']} units", f"-{omar_metrics['Units Lost vs Nathan']} vs Nathan")
        st.metric("Omar Labor Cost", omar_metrics["Labor Cost"], f"{omar_metrics['Extra Cost vs Nathan']} extra")
        st.metric("Cost per Unit", omar_metrics["Cost/Unit"], f"vs Nathan ${NATE_COST_PER_UNIT_HIST:.4f}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_o2:
        fig_o = go.Figure()
        fig_o.add_trace(go.Bar(name="Omar", x=["Units/Hr"], y=[OMAR_UNITS_HR], marker_color="#ef4444"))
        fig_o.add_trace(go.Bar(name="Nathan", x=["Units/Hr"], y=[nate_combined], marker_color="#22c55e"))
        fig_o.update_layout(title="Units per Hour: Omar vs Nathan", barmode="group", height=280)
        st.plotly_chart(fig_o, use_container_width=True)

# TAB 2: Team vs Nathan
with tab2:
    st.subheader("Full Team vs Nathan (3-person equivalent)")
    col_t1, col_t2, col_t3 = st.columns([1, 2, 1])
    
    with col_t1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Team Units Produced", f"{team_metrics['Units Produced']} units", f"-{team_metrics['Units Lost vs Nathan']} vs Nathan")
        st.metric("Team Labor Cost", team_metrics["Labor Cost"], f"{team_metrics['Extra Cost vs Nathan']} extra")
        st.metric("Team Cost/Unit", team_metrics["Cost/Unit"], f"vs Nathan ${NATE_COST_PER_UNIT_HIST:.4f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_t2:
        st.markdown("**Productivity Multiplier**")
        st.metric("Team is slower by", team_metrics["Productivity Ratio (× Nathan)"], "lower output")
        st.caption(f"In {comparison_hours} hours the team produces **{team_metrics['Units Produced']}** units while Nathan alone would produce **{nate_combined * comparison_hours:.1f}** units if he replaced all three.")
    
    with col_t3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Profitability (Units per $)", f"{team_metrics['Units/$']}", f"vs Nathan {nate_baseline['Units/$']}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Pack comparison (Nathan only)
    st.divider()
    st.subheader("Packing Station Loss (Nathan’s specialty)")
    pack_loss_units = nate_pack * comparison_hours
    st.metric("Units the Team could have packed (at Nathan’s rate)", f"{pack_loss_units:,.0f} units", "Team packed 0 during talk time")
    st.caption("Nathan’s pack rate = 88 units every 47 minutes = 112.34/hr")

# TAB 3: Visual Dashboard
with tab3:
    st.subheader("Profitability & Loss Overview")
    
    # DataFrame for all
    all_data = [
        nate_baseline,
        david_metrics,
        omar_metrics,
        dylan_metrics,
        team_metrics
    ]
    df = pd.DataFrame(all_data)
    
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Units Lost vs Nathan": st.column_config.NumberColumn(format="%.1f", help="Opportunity loss in units"),
            "Extra Cost vs Nathan": st.column_config.TextColumn(),
            "Profitability Gap": st.column_config.TextColumn()
        }
    )
    
    # Profitability bar chart
    fig_profit = go.Figure()
    names = df["Name"].tolist()
    units_per_dollar = df["Units/$"].tolist()
    
    fig_profit.add_trace(go.Bar(
        x=names,
        y=units_per_dollar,
        marker_color=["#22c55e" if n == "Nathan (baseline)" else "#ef4444" for n in names],
        text=[f"{x:.3f}" for x in units_per_dollar],
        textposition="auto"
    ))
    fig_profit.update_layout(
        title="Units per Labor Dollar – Profitability Comparison",
        yaxis_title="Units Produced per $ Spent",
        height=420,
        bargap=0.3
    )
    st.plotly_chart(fig_profit, use_container_width=True)
    
    st.success(f"**Key Insight**: In {comparison_hours} hours, the team loses **{team_metrics['Units Lost vs Nathan']:,.0f} units** and pays **{team_metrics['Extra Cost vs Nathan']}** more in labor compared to Nathan-level productivity.")

# ====================== FOOTER ======================
st.caption("""
Nathan historical: 30.29 hrs • 1,802 stow units • Pick 59–155/hr (avg 107) • Pack 112.34/hr  
All calculations use **pick + stow combined** for fair apples-to-apples comparison.  
Dylan uses David’s historical rate. Talk-time context preserved but fully adjustable.
""")
st.success("✅ Live competitive tool • Adjust hours or Nathan rates in sidebar for real-time updates")
```​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​
