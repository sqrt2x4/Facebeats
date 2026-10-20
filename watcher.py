import os
import time
import subprocess

retraining = False
last_state = {}

DATASET_PATH = "dataset"


def scan_dataset():
    state = {}

    for user in os.listdir(DATASET_PATH):
        user_path = os.path.join(DATASET_PATH, user)

        if not os.path.isdir(user_path):
            continue

        state[user] = len(os.listdir(user_path))

    return state


def retrain_safe():
    global retraining

    if retraining:
        return

    retraining = True

    print("Training model...")
    subprocess.run(["python3", "retrain.py"])

    print("✅ Training complete!")
    retraining = False


print("👀 Watching dataset for changes...")

last_state = scan_dataset()

while True:
    time.sleep(3)

    current_state = scan_dataset()

    if current_state != last_state:
        print("📦 Dataset changed → retraining...")
        retrain_safe()
        last_state = current_state