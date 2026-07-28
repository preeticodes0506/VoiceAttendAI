import os
import librosa
import numpy as np
import joblib
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.ensemble import RandomForestClassifier

# ===========================================
# DATASET PATH
# ===========================================

DATASET_PATH = "voice_samples"

X = []
y = []

# ===========================================
# READ DATASET
# ===========================================

for student in sorted(os.listdir(DATASET_PATH)):

    student_path = os.path.join(DATASET_PATH, student)

    if not os.path.isdir(student_path):
        continue

    print(f"Reading Student {student}")

    for file in sorted(os.listdir(student_path)):

        if not file.endswith(".wav"):
            continue

        file_path = os.path.join(student_path, file)

        signal, sr = librosa.load(file_path, sr=22050)

        mfcc = librosa.feature.mfcc(
            y=signal,
            sr=sr,
            n_mfcc=40
        )

        feature = np.concatenate([
            np.mean(mfcc, axis=1),
            np.std(mfcc, axis=1)
        ])

        X.append(feature)
        y.append(student)

# ===========================================
# CONVERT TO NUMPY
# ===========================================

X = np.array(X)
y = np.array(y)

print("\n==============================")
print("Total Samples :", len(X))
print("Feature Size :", X.shape[1])
print("==============================\n")

# ===========================================
# TRAIN TEST SPLIT
# ===========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

# ===========================================
# FEATURE SCALING
# ===========================================

scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

os.makedirs("models", exist_ok=True)

joblib.dump(
    scaler,
    "models/scaler.pkl"
)

# ===========================================
# RANDOM FOREST
# ===========================================

print("Training Model...\n")

model = RandomForestClassifier(

    n_estimators=500,

    max_depth=30,

    min_samples_split=2,

    min_samples_leaf=1,

    random_state=42

)

model.fit(X_train, y_train)

# ===========================================
# TEST MODEL
# ===========================================

y_pred = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    y_pred
)

print("="*40)
print(f"Model Accuracy : {accuracy*100:.2f}%")
print("="*40)

# ===========================================
# SAVE MODEL
# ===========================================

joblib.dump(
    model,
    "models/voice_model.pkl"
)

print("\nModel Saved Successfully!")

# ===========================================
# CONFUSION MATRIX
# ===========================================

cm = confusion_matrix(
    y_test,
    y_pred
)

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=np.unique(y)
)

disp.plot(cmap="Blues")

plt.title("Voice Recognition Confusion Matrix")

plt.show()