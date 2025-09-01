import streamlit as st
import pandas as pd
import numpy as np

@st.cache_data
def load_data():
    """Load workout records and workout data from CSV files."""
    df_records = pd.read_csv('filtered_records.csv', parse_dates=['start_date', 'end_date'])
    df_workouts = pd.read_csv('filtered_workouts.csv', parse_dates=['start_date', 'end_date'])
    return df_records, df_workouts

def make_sessions_table(df_records, df_workouts):
    """
    Organize aggregate metrics for each workout session.
    
    Args:
        df_records: DataFrame with individual workout records
        df_workouts: DataFrame with workout session information
        
    Returns:
        DataFrame with aggregated workout sessions and metrics
    """
    # Keep all records that are linked to a workout_id
    df_rec = df_records[df_records['workout_id'].notna()].copy()
    df_rec['workout_id'] = df_rec['workout_id'].astype(int)
    df_workouts['workout_id'] = df_workouts['workout_id'].astype(int)

    # Restrict workouts to ONLY those that have at least one record
    ids_with_records = df_rec['workout_id'].unique()
    sess = df_workouts[df_workouts['workout_id'].isin(ids_with_records)].copy()

    # Base columns
    sess = sess[['workout_id','start_date','end_date','activity_type','duration']].copy()
    sess['duration'] = pd.to_numeric(sess['duration'], errors='coerce')

    # Aggregates per workout_id
    active = df_rec[df_rec['metric']=="active_calories"].groupby('workout_id')['value'].sum().rename('active_calories')
    basal  = df_rec[df_rec['metric']=="basal_calories"].groupby('workout_id')['value'].sum().rename('basal_calories')
    steps  = df_rec[df_rec['metric']=="steps"].groupby('workout_id')['value'].sum().rename('total_steps')
    dist   = df_rec[df_rec['metric']=="distance"].groupby('workout_id')['value'].sum().rename('total_distance')
    hr     = df_rec[df_rec['metric']=="heart_rate"].groupby('workout_id')['value'].mean().rename('avg_hr')

    # Merge metrics
    for s in [active, basal, steps, dist, hr]:
        sess = sess.merge(s, on='workout_id', how='left')

    # Fill only additive metrics
    sess['active_calories'] = sess['active_calories'].fillna(0)
    sess['basal_calories']  = sess['basal_calories'].fillna(0)
    sess['total_steps']     = sess['total_steps'].fillna(0)
    sess['total_distance']  = sess['total_distance'].fillna(0)

    # Calculated metrics
    sess['total_cals']  = sess['active_calories'] + sess['basal_calories']
    sess['cal_per_min'] = np.where(sess['duration']>0, sess['total_cals']/sess['duration'], np.nan)

    # Date columns for filtering and grouping
    sess['date']  = sess['start_date'].dt.date
    sess['month'] = sess['start_date'].dt.month
    sess['year']  = sess['start_date'].dt.year

    # Drop sessions with no calories (invalid/incomplete sessions)
    sess = sess[sess['total_cals'] > 0]

    return sess