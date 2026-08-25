"""
train_ann.py  (ENHANCED)
-------------------------
Trains an Artificial Neural Network (ANN) using TensorFlow/Keras to
predict student performance category: Good / Average / Poor.

Architecture:
    Input (8 features)
      -> Dense 64, ReLU
      -> Dense 32, ReLU
      -> Dense 16, ReLU
      -> Output Dense 3, Softmax

NEW in this version:
  - Saves accuracy-vs-epoch and loss-vs-epoch training curves as PNG
    images. These are excellent evidence in a viva that the network
    actually learned (not just a final-number claim) and that it
    isn't overfitting (train vs validation curves stay close).

Run:
    python train_ann.py
Outputs:
    models/ann_model.keras
    models/scaler.pkl        (kept consistent with Random Forest)
    reports/ann_training_curves.png
"""

import os
import numpy as np
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split

from preprocessing import load_dataset, fit_scaler, LABEL_COLUMN, LABEL_ORDER

os.makedirs("reports", exist_ok=True)

tf.random.set_seed(42)
np.random.seed(42)

print("Loading and preprocessing dataset...")
df = load_dataset()

scaler, X_scaled = fit_scaler(df)

# Encode labels in FIXED order: Good=0, Average=1, Poor=2
label_to_idx = {label: i for i, label in enumerate(LABEL_ORDER)}
y_idx = df[LABEL_COLUMN].map(label_to_idx).values
y_onehot = to_categorical(y_idx, num_classes=3)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_onehot, test_size=0.2, random_state=42
)

print("Building ANN model...")
model = Sequential([
    Input(shape=(X_scaled.shape[1],)),
    Dense(64, activation="relu"),
    Dense(32, activation="relu"),
    Dense(16, activation="relu"),
    Dense(3, activation="softmax"),
])

model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
model.summary()

print("\nTraining ANN...")
history = model.fit(
    X_train, y_train,
    validation_split=0.15,
    epochs=60,
    batch_size=16,
    verbose=2,
)

loss, acc = model.evaluate(X_test, y_test, verbose=0)
print(f"\nTest Accuracy: {acc*100:.2f}%  |  Test Loss: {loss:.4f}")

# ------------------------------------------------------------------
# Save training curves — accuracy & loss vs epoch (train vs val)
# ------------------------------------------------------------------
h = history.history
epochs_range = range(1, len(h["accuracy"]) + 1)

fig, axes = plt.subplots(1, 2, figsize=(11, 4))

axes[0].plot(epochs_range, h["accuracy"], label="Train Accuracy", color="#3454D1")
axes[0].plot(epochs_range, h["val_accuracy"], label="Validation Accuracy", color="#0EA894")
axes[0].set_xlabel("Epoch")
axes[0].set_ylabel("Accuracy")
axes[0].set_title("ANN Accuracy over Training")
axes[0].legend()

axes[1].plot(epochs_range, h["loss"], label="Train Loss", color="#3454D1")
axes[1].plot(epochs_range, h["val_loss"], label="Validation Loss", color="#E1524F")
axes[1].set_xlabel("Epoch")
axes[1].set_ylabel("Loss")
axes[1].set_title("ANN Loss over Training")
axes[1].legend()

plt.tight_layout()
plt.savefig("reports/ann_training_curves.png", dpi=150)
plt.close()
print("Saved reports/ann_training_curves.png")

model.save("models/ann_model.keras")
joblib.dump(scaler, "models/scaler.pkl")  # keep scaler consistent across models
print("\nSaved models/ann_model.keras")
print("Label order used for output neurons:", LABEL_ORDER)
