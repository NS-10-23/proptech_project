import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import joblib

os.makedirs('dataset', exist_ok=True)
os.makedirs('valuation/ml_models', exist_ok=True)

print("1. Generating Large-Scale Nepal Real Estate Dataset...")
np.random.seed(42)
n_samples = 6000

locations = [
    'Baluwatar, Kathmandu',
    'New Baneshwor, Kathmandu',
    'Jhamsikhel, Lalitpur',
    'Budhanilkantha, Kathmandu',
    'Koteshwor, Kathmandu',
    'Imadol, Lalitpur',
    'Suryabinayak, Bhaktapur',
    'Maharajgunj, Kathmandu',
    'Sanepa, Lalitpur'
]

# Wide-scale properties: from 1 Aana up to 120 Aana (commercial/multi-ropani)
land_aana = np.random.exponential(scale=12, size=n_samples) + 1.5
land_aana = np.clip(land_aana, 1.0, 150.0).round(2)

# Floors from 1 up to 15 floors (houses to commercial towers)
floors = np.clip(np.random.choice(np.arange(1.0, 16.0, 0.5), size=n_samples), 1.0, 15.0)

# Road width from 6 feet up to 80 feet (highways/main roads)
road_feet = np.random.choice(np.arange(6, 82, 2), size=n_samples)
road_type = np.random.choice(['Pitch', 'Concrete', 'Gravel'], size=n_samples)

# Rooms and Bathrooms scale with floors and size
rooms = np.clip(np.round(floors * 3.5 + np.random.randint(1, 6, size=n_samples)), 2, 80).astype(int)
bathrooms = np.clip(np.round(rooms * 0.6), 1, 50).astype(int)
selected_locs = np.random.choice(locations, size=n_samples)

# Valuation Rates per Aana in NPR
aana_rates = {
    'Baluwatar, Kathmandu': 7500000,
    'Maharajgunj, Kathmandu': 7200000,
    'Jhamsikhel, Lalitpur': 7000000,
    'Sanepa, Lalitpur': 6800000,
    'New Baneshwor, Kathmandu': 6500000,
    'Koteshwor, Kathmandu': 4800000,
    'Budhanilkantha, Kathmandu': 4200000,
    'Imadol, Lalitpur': 3500000,
    'Suryabinayak, Bhaktapur': 2800000
}

land_value = np.array([aana_rates[loc] for loc in selected_locs]) * land_aana
# Construction cost ~Rs. 35 Lakhs per floor per standard size
construction_value = (floors * 3800000) + (rooms * 250000)
road_multiplier = 1 + (road_feet - 10) * 0.015

total_price_npr = (land_value + construction_value) * road_multiplier + np.random.normal(0, 1000000, size=n_samples)
total_price_npr = np.round(total_price_npr, -5)

data = pd.DataFrame({
    'location': selected_locs,
    'land_aana': land_aana,
    'floors': floors,
    'road_feet': road_feet,
    'road_type': road_type,
    'rooms': rooms,
    'bathrooms': bathrooms,
    'price_npr': total_price_npr
})

csv_path = 'dataset/nepal_gharjagga_data.csv'
data.to_csv(csv_path, index=False)
print(f"-> Saved wide-scale dataset to '{csv_path}'")

# Train Random Forest Pipeline
X = data[['location', 'land_aana', 'floors', 'road_feet', 'road_type', 'rooms', 'bathrooms']]
y = data['price_npr']

preprocessor = ColumnTransformer(transformers=[
    ('num', StandardScaler(), ['land_aana', 'floors', 'road_feet', 'rooms', 'bathrooms']),
    ('cat', OneHotEncoder(handle_unknown='ignore'), ['location', 'road_type'])
])

pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('model', RandomForestRegressor(n_estimators=150, max_depth=20, random_state=42, n_jobs=-1))
])

print("2. Training Model on Wide Scale Data...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
pipeline.fit(X_train, y_train)

print(f"-> Accuracy R2: {pipeline.score(X_test, y_test) * 100:.2f}%")

model_path = 'valuation/ml_models/nepal_gharjagga_model.joblib'
joblib.dump(pipeline, model_path)
print(f"-> Success! Wide-scale model saved to '{model_path}'")