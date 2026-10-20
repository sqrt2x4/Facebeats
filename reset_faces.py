import os
import shutil

# delete model file
if os.path.exists("trainer.yml"):
    os.remove("trainer.yml")
    print("Deleted trainer.yml")

# delete labels file
if os.path.exists("labels.txt"):
    os.remove("labels.txt")
    print("Deleted labels.txt")

# delete dataset folder
if os.path.exists("dataset"):
    shutil.rmtree("dataset")
    print("Deleted dataset folder")

print("Face recognition reset complete.")