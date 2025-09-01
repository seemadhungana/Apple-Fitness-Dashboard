import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_processing import load_data, make_sessions_table
from visualizations import build_calendar_heatmap

st.set_page_config(page_title="Workout Dashboard", layout="wide")

# Load and process data
df_records, df_workouts = load_data()
sessions = make_sessions_table(df_records, df_workouts)

# --- SIDEBAR ---
st.sidebar.header("Filters")

years = sorted(sessions["year"].dropna().unique())
year = st.sidebar.selectbox("Year", years, index=len(years)-1)

months = sessions[sessions["year"]==year]["month"].dropna().unique()
month_names = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
month = st.sidebar.selectbox("Month", sorted(months), format_func=lambda m: month_names[int(m)])

types = ["All"] + sorted([t for t in sessions["activity_type"].dropna().unique()])
atype = st.sidebar.selectbox("Activity type", types)

# Filter data
filtered = sessions[(sessions["year"]==year) & (sessions["month"]==month)]
if atype != "All":
    filtered = filtered[filtered["activity_type"]==atype]

# --- MAIN DASHBOARD ---
st.markdown(f"### {month_names[int(month)]} {year}")

# Metrics row
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Workouts", int(filtered["workout_id"].nunique()))
k2.metric("Total Calories", f"{filtered['total_cals'].sum():.0f}")
k3.metric("Avg HR", f"{filtered['avg_hr'].mean():.0f}" if filtered["avg_hr"].notna().any() else "—")
k4.metric("Total Distance", f"{filtered['total_distance'].sum():.2f}")
k5.metric("Total Steps", f"{filtered['total_steps'].sum():.0f}")
k6.metric("Avg Duration", f"{filtered['duration'].mean():.0f} min")

# Calendar heatmap
daily = filtered.groupby("date").agg(total_cals=("total_cals","sum")).reset_index()
cal_map = {row["date"]: row["total_cals"] for _, row in daily.iterrows()}
fig_cal = build_calendar_heatmap(year, month, cal_map)
st.plotly_chart(fig_cal, use_container_width=True)

# Scatter plot: Calories vs Duration
if not filtered.empty:
    fig_sc = px.scatter(
        filtered.sort_values("start_date"),
        x="duration", y="total_cals", color="activity_type",
        size=(filtered["avg_hr"].clip(lower=filtered["avg_hr"].quantile(0.1), upper=filtered["avg_hr"].quantile(0.9)) if filtered["avg_hr"].notna().any() else None),
        hover_data={"start_date": True, "avg_hr": True, "total_distance": True, "total_steps": True, "workout_id": True},
        title="Calories vs Duration (per workout)"
    )
    st.plotly_chart(fig_sc, use_container_width=True)

# Stacked bar chart: Active vs Basal Calories
comp = filtered.sort_values("start_date")[["workout_id","start_date","active_calories","basal_calories","activity_type"]].copy()
comp["date_label"] = comp["start_date"].dt.strftime("%b %d %H:%M")

fig_stacked = go.Figure()
fig_stacked.add_bar(x=comp["date_label"], y=comp["active_calories"], name="Active")
fig_stacked.add_bar(x=comp["date_label"], y=comp["basal_calories"], name="Basal")
fig_stacked.update_layout(barmode="stack", title="Active vs Basal Calories (per workout)", xaxis_title="Workout (chronological)", yaxis_title="Calories")
st.plotly_chart(fig_stacked, use_container_width=True)

# Workout selector and details
opts = filtered.sort_values("start_date")[["workout_id","start_date","activity_type","total_cals","duration"]]
opts["label"] = opts.apply(lambda r: f"{r.start_date.strftime('%b %d %I:%M %p')} — {r.activity_type} ({int(r.total_cals)} kcal, {int(r.duration)} min)", axis=1)
choice = st.selectbox("Select a workout for details", opts["label"].tolist()) if not opts.empty else None

if choice:
    wid = int(opts.iloc[opts["label"].tolist().index(choice)]["workout_id"])
    sess_row = filtered[filtered["workout_id"]==wid].iloc[0]

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Total kcal", f"{int(sess_row.total_cals)}")
    c2.metric("Active", f"{int(sess_row.active_calories)}")
    c3.metric("Basal", f"{int(sess_row.basal_calories)}")
    c4.metric("Duration", f"{int(sess_row.duration)} min")
    c5.metric("Avg HR", f"{int(sess_row.avg_hr) if pd.notna(sess_row.avg_hr) else 0}")
    c6.metric("Distance", f"{sess_row.total_distance:.2f}")

    # HR timeline (if available)
    hr_session = df_records[(df_records["workout_id"]==wid) & (df_records["metric"]=="heart_rate")][["start_date","value"]].sort_values("start_date")
    if not hr_session.empty:
        fig_hr = px.line(hr_session, x="start_date", y="value", title="Heart Rate (session timeline)", markers=True)
        st.plotly_chart(fig_hr, use_container_width=True)