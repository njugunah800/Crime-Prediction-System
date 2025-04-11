import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load dataset
df = pd.read_csv("Datasets/Kiambu Dataset.csv")
df.columns = df.columns.str.strip()  # Clean column names

# Define crime types
crime_columns = ['Murder', 'Kidnapping', 'Sexual_Crimes', 'Assault', 'Theft', 'Cyber_Crimes']

# Initialize a new DataFrame to collect training records
records = []

# Generate training data for EACH crime type per location
for crime in crime_columns:
    for location in df['Location'].unique():
        total = df[df['Location'] == location][crime].sum()
        records.append({
            'Location': location,
            'Crime_Type': crime,
            'Total': total
        })

# Add 'All' crime type by summing everything for all locations from 2000-2023
for location in df['Location'].unique():
    total = df[df['Location'] == location][crime_columns].sum().sum()  # Sum all crime types
    records.append({
        'Location': location,
        'Crime_Type': 'All',
        'Total': total
    })

# Create a training DataFrame
train_df = pd.DataFrame(records)

# Label encode Location and Crime_Type
location_encoder = LabelEncoder()
train_df['Location_Encoded'] = location_encoder.fit_transform(train_df['Location'])

crime_encoder = LabelEncoder()
train_df['Crime_Encoded'] = crime_encoder.fit_transform(train_df['Crime_Type'])

# Generate labels (High, Moderate, Low) based on quantiles of total crimes across all locations
def get_level(value, col):
    if value > col.quantile(0.75):
        return "High"
    elif value > col.quantile(0.25):
        return "Moderate"
    else:
        return "Low"

# Apply quantile classification to the 'Total' column
train_df['Crime_Level'] = train_df['Total'].apply(lambda x: get_level(x, train_df['Total']))

# Features and labels
X = train_df[['Location_Encoded', 'Crime_Encoded', 'Total']]
y = train_df['Crime_Level']

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# Evaluate model
preds = model.predict(X_test_scaled)
acc = accuracy_score(y_test, preds)
print(f"✅ Accuracy: {acc*100:.2f}%")

# Save the trained model and encoders
joblib.dump(model, "crime_prediction_model.pkl")
joblib.dump(location_encoder, "location_encoder.pkl")
joblib.dump(crime_encoder, "crime_encoder.pkl")
joblib.dump(scaler, "scaler.pkl")

print("✅ Model, encoder & scaler saved!")
