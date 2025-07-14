# setup_model.py

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib
import os

# Create output directory if not exists
os.makedirs("model", exist_ok=True)

# Generate dummy training data
X = np.random.rand(100, 8)
y = np.random.rand(100, 1)

# Build and train a simple model
model = Sequential([
    Dense(64, activation='relu', input_shape=(8,)),
    Dense(1)
])
model.compile(optimizer='adam', loss='mse')
model.fit(X, y, epochs=5)

# Save model
model.save("model/model.h5", save_format="h5")

print("✅ Model saved at model/model.h5")

# Create and save scaler
scaler = StandardScaler()
scaler.fit(X)
joblib.dump(scaler, "model/scaler.save")
print("✅ Scaler saved at model/scaler.save")
