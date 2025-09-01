import xml.etree.ElementTree as ET
import pandas as pd

tree = ET.parse("apple_health_export/export.xml")
root = tree.getroot()

# extract workout data
workout_data = [w.attrib for w in root.findall("Workout")]
df_workouts = pd.DataFrame(workout_data)
df_workouts['start_date'] = pd.to_datetime(df_workouts['startDate'])
df_workouts['end_date'] = pd.to_datetime(df_workouts['endDate'])

# extract record data
record_data = [r.attrib for r in root.findall("Record")]
df_records = pd.DataFrame(record_data)
df_records['start_date'] = pd.to_datetime(df_records['startDate'])
df_records['end_date'] = pd.to_datetime(df_records['endDate'])

# create workout_id
df_workouts = df_workouts.copy()
df_workouts['workout_id'] = range(len(df_workouts))

# assign matching workout_id to each record
df_records = df_records.copy()
df_records['workout_id'] = None

for _, workout in df_workouts.iterrows():
    start = workout['start_date']
    end = workout['end_date']
    wid = workout['workout_id']

    mask = (df_records['start_date'] >= start) & (df_records['end_date'] <= end)
    df_records.loc[mask, 'workout_id'] = wid

# CLEAN WORKOUT DATA
# only keep relevant columns in workouts
workouts_columns_to_keep = ['workoutActivityType', 'duration', 'durationUnit', 'start_date', 'end_date', 'workout_id']
filtered_workouts = df_workouts.copy()
filtered_workouts = filtered_workouts[workouts_columns_to_keep]

rename_workouts = {
    'HKWorkoutActivityTypeCoreTraining':'core_training',
    'HKWorkoutActivityTypeCardioDance':'cardio_dance',
    'HKWorkoutActivityTypeFunctionalStrengthTraining':'functional_strength_training',
    'HKWorkoutActivityTypeYoga':'yoga',
    'HKWorkoutActivityTypeWalking':'walking',
    'HKWorkoutActivityTypeElliptical':'elliptical',
    'HKWorkoutActivityTypeBoxing':'boxing',
    'HKWorkoutActivityTypeRunning':'running',
    'HKWorkoutActivityTypeStairClimbing':'stair_climbing'
}

filtered_workouts['workoutActivityType'] = filtered_workouts['workoutActivityType'].map(rename_workouts)
filtered_workouts = filtered_workouts.rename(columns={'workoutActivityType':'activity_type', 'durationUnit':'duration_unit'})
filtered_workouts.head()

# CLEAN RECORDS DATA
# only keep records that fall within workouts
df_records = df_records[df_records['workout_id'].notnull()].copy()
records_columns_to_keep = ['type', 'unit', 'start_date', 'end_date', 'value', 'workout_id']
df_records = df_records[records_columns_to_keep].sort_values(by='workout_id')

# filter for only data types in records
relevant_data = {
    'HKQuantityTypeIdentifierHeartRate': 'heart_rate',
    'HKQuantityTypeIdentifierStepCount': 'steps',
    'HKQuantityTypeIdentifierDistanceWalkingRunning': 'distance',
    'HKQuantityTypeIdentifierBasalEnergyBurned': 'basal_calories',
    'HKQuantityTypeIdentifierActiveEnergyBurned': 'active_calories'
}

# filter and copy the data
filtered_records = df_records[df_records['type'].isin(relevant_data.keys())].copy()

# convert 'value' to float
filtered_records['value'] = filtered_records['value'].astype(float)

# rename 'type' values to user-friendly names
filtered_records['type'] = filtered_records['type'].map(relevant_data)
filtered_records = filtered_records.rename(columns={'type': 'metric'})
filtered_records.head()

# Save filtered records
filtered_records.to_csv("filtered_records.csv", index=False)

# Save filtered workouts
filtered_workouts.to_csv("filtered_workouts.csv", index=False)