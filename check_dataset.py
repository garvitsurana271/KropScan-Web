# check_dataset.py
import os

dataset_path = "New Plant Diseases Dataset(Augmented)"

if os.path.exists(dataset_path):
    train_path = os.path.join(dataset_path, "train")
    valid_path = os.path.join(dataset_path, "valid")
    
    if os.path.exists(train_path) and os.path.exists(valid_path):
        train_classes = os.listdir(train_path)
        print(f"✅ Dataset found!")
        print(f"✅ Training classes: {len(train_classes)}")
        print(f"\n🌿 Sample classes:")
        for i, cls in enumerate(train_classes[:5]):
            num_images = len(os.listdir(os.path.join(train_path, cls)))
            print(f"   {i+1}. {cls}: {num_images} images")
    else:
        print("❌ Train/Valid folders not found!")
else:
    print("❌ Dataset folder not found!")
    print(f"Looking for: {os.path.abspath(dataset_path)}")