import os
import cv2
import face_recognition
import pickle

DATASET_PATH = "face_dataset"
ENCODINGS_FILE = "face_encodings.pkl"

known_encodings = []
known_names = []

for person_name in os.listdir(DATASET_PATH):
    person_path = os.path.join(DATASET_PATH, person_name)
    
    if not os.path.isdir(person_path):
        continue

    for image_name in os.listdir(person_path):
        image_path = os.path.join(person_path, image_name)
        image = cv2.imread(image_path)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        encodings = face_recognition.face_encodings(rgb_image)
        if len(encodings) > 0:
            known_encodings.append(encodings[0])
            known_names.append(person_name)

data = {"encodings": known_encodings, "names": known_names}

with open(ENCODINGS_FILE, "wb") as f:
    pickle.dump(data, f)

print(f"✅ Training complete. {len(known_names)} faces encoded.")
