# prepare_plantdoc_dataset.py - FIXED FOR SUBFOLDER STRUCTURE
import os
import shutil
from pathlib import Path
import json
from collections import defaultdict
import random
from PIL import Image
import numpy as np
from tqdm import tqdm

print("="*80)
print("🌾 KROPSCAN ULTIMATE DATASET - PlantDoc + PlantVillage")
print("="*80)

# Paths
PLANTDOC_DIR = 'PlantDoc-Dataset-master'
PLANTVILLAGE_TRAIN = 'New Plant Diseases Dataset(Augmented)/train'
PLANTVILLAGE_VAL = 'New Plant Diseases Dataset(Augmented)/valid'
OUTPUT_DIR = 'KropScan_Ultimate_Dataset'

# Verify
print(f"\n🔍 Verifying paths...")
if not os.path.exists(PLANTDOC_DIR):
    print(f"   ❌ PlantDoc not found: {PLANTDOC_DIR}")
    exit()
else:
    print(f"   ✅ PlantDoc found")

if not os.path.exists(PLANTVILLAGE_TRAIN):
    print(f"   ❌ PlantVillage not found: {PLANTVILLAGE_TRAIN}")
    exit()
else:
    print(f"   ✅ PlantVillage found")

# Class name mapping - PlantDoc folder names to standard format
CLASS_MAPPING = {
    # Tomato
    'tomato early blight leaf': 'Tomato___Early_blight',
    'tomato early blight': 'Tomato___Early_blight',
    'tomato leaf early blight': 'Tomato___Early_blight',
    
    'tomato late blight leaf': 'Tomato___Late_blight',
    'tomato late blight': 'Tomato___Late_blight',
    'tomato leaf late blight': 'Tomato___Late_blight',
    
    'tomato healthy leaf': 'Tomato___healthy',
    'tomato healthy': 'Tomato___healthy',
    'tomato leaf': 'Tomato___healthy',
    
    'tomato septoria leaf spot': 'Tomato___Septoria_leaf_spot',
    'tomato septoria leaf spot leaf': 'Tomato___Septoria_leaf_spot',
    
    'tomato leaf bacterial spot': 'Tomato___Bacterial_spot',
    'tomato bacterial spot': 'Tomato___Bacterial_spot',
    
    'tomato two spotted spider mites leaf': 'Tomato___Spider_mites',
    'tomato spider mites': 'Tomato___Spider_mites',
    
    'tomato leaf yellow virus': 'Tomato___Yellow_Leaf_Curl_Virus',
    'tomato yellow leaf curl virus': 'Tomato___Yellow_Leaf_Curl_Virus',
    
    'tomato mold leaf': 'Tomato___Leaf_Mold',
    'tomato leaf mold': 'Tomato___Leaf_Mold',
    
    'tomato leaf mosaic virus': 'Tomato___Tomato_mosaic_virus',
    'tomato mosaic virus': 'Tomato___Tomato_mosaic_virus',
    
    # Potato
    'potato leaf early blight': 'Potato___Early_blight',
    'potato early blight': 'Potato___Early_blight',
    
    'potato leaf late blight': 'Potato___Late_blight',
    'potato late blight': 'Potato___Late_blight',
    
    'potato leaf': 'Potato___healthy',
    'potato healthy': 'Potato___healthy',
    
    # Pepper
    'bell_pepper leaf': 'Pepper,_bell___healthy',
    'bell pepper leaf': 'Pepper,_bell___healthy',
    'pepper bell leaf': 'Pepper,_bell___healthy',
    
    'bell_pepper leaf spot': 'Pepper,_bell___Bacterial_spot',
    'bell pepper leaf spot': 'Pepper,_bell___Bacterial_spot',
    'pepper bell bacterial spot': 'Pepper,_bell___Bacterial_spot',
    
    # Apple
    'apple scab leaf': 'Apple___Apple_scab',
    'apple apple scab': 'Apple___Apple_scab',
    
    'apple rust leaf': 'Apple___Cedar_apple_rust',
    'apple cedar apple rust': 'Apple___Cedar_apple_rust',
    
    'apple leaf': 'Apple___healthy',
    'apple healthy': 'Apple___healthy',
    
    # Corn
    'corn leaf blight': 'Corn_(maize)___Northern_Leaf_Blight',
    'corn northern leaf blight': 'Corn_(maize)___Northern_Leaf_Blight',
    
    'corn gray leaf spot': 'Corn_(maize)___Cercospora_leaf_spot',
    'corn cercospora leaf spot': 'Corn_(maize)___Cercospora_leaf_spot',
    
    'corn common rust': 'Corn_(maize)___Common_rust',
    'corn rust': 'Corn_(maize)___Common_rust',
    
    # Grape
    'grape leaf': 'Grape___healthy',
    'grape healthy': 'Grape___healthy',
    
    'grape leaf black rot': 'Grape___Black_rot',
    'grape black rot': 'Grape___Black_rot',
    
    # Others
    'blueberry leaf': 'Blueberry___healthy',
    'cherry leaf': 'Cherry_(including_sour)___healthy',
    'peach leaf': 'Peach___healthy',
    'raspberry leaf': 'Raspberry___healthy',
    'soybean leaf': 'Soybean___healthy',
    'soyabean leaf': 'Soybean___healthy',
    'strawberry leaf': 'Strawberry___healthy',
}

def normalize_folder_name(folder_name):
    """Normalize PlantDoc folder name to standard class"""
    normalized = folder_name.lower().strip()
    
    # Direct match
    if normalized in CLASS_MAPPING:
        return CLASS_MAPPING[normalized]
    
    # Try without underscores
    normalized_clean = normalized.replace('_', ' ')
    if normalized_clean in CLASS_MAPPING:
        return CLASS_MAPPING[normalized_clean]
    
    # Fuzzy match - check if key words are present
    for key, value in CLASS_MAPPING.items():
        if key in normalized or normalized in key:
            return value
    
    # Word-by-word matching
    words = set(normalized.replace('_', ' ').split())
    for key, value in CLASS_MAPPING.items():
        key_words = set(key.split())
        if len(words & key_words) >= 2:  # At least 2 words match
            return value
    
    return None

def check_image_quality(image_path):
    """Check if image is valid and good quality"""
    try:
        img = Image.open(image_path)
        img.verify()
        img = Image.open(image_path)  # Reopen after verify
        
        width, height = img.size
        
        # Size check
        if width < 50 or height < 50:
            return False, "too_small"
        
        # Convert to RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Basic quality checks
        img_array = np.array(img)
        
        # Brightness
        mean_brightness = img_array.mean()
        if mean_brightness < 10 or mean_brightness > 250:
            return False, "bad_exposure"
        
        # Variance (not blank)
        if img_array.std() < 5:
            return False, "low_variance"
        
        return True, "ok"
        
    except Exception as e:
        return False, "corrupted"

def process_plantdoc():
    """Process PlantDoc dataset with subfolder structure"""
    print(f"\n{'='*80}")
    print(f"📊 PROCESSING PLANTDOC DATASET")
    print(f"{'='*80}")
    
    plantdoc_images = defaultdict(list)
    stats = {
        'total_folders': 0,
        'total_images': 0,
        'processed': 0,
        'mapped': 0,
        'unmapped': 0,
        'errors': 0,
        'unmapped_folders': []
    }
    
    # Process train and test splits
    for split in ['train', 'test']:
        split_path = os.path.join(PLANTDOC_DIR, split)
        
        if not os.path.exists(split_path):
            print(f"   ⚠️ {split}/ not found")
            continue
        
        print(f"\n   📁 Processing {split}/")
        
        # Get all subfolders (classes)
        class_folders = [f for f in os.listdir(split_path) if os.path.isdir(os.path.join(split_path, f))]
        stats['total_folders'] += len(class_folders)
        
        print(f"      Found {len(class_folders)} class folders")
        
        for class_folder in tqdm(class_folders, desc=f"      {split} classes"):
            class_path = os.path.join(split_path, class_folder)
            
            # Map folder name to standard class
            standard_class = normalize_folder_name(class_folder)
            
            if not standard_class:
                stats['unmapped'] += 1
                stats['unmapped_folders'].append(class_folder)
                continue
            
            # Process all images in this class folder
            image_files = [f for f in os.listdir(class_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            stats['total_images'] += len(image_files)
            
            for img_file in image_files:
                img_path = os.path.join(class_path, img_file)
                
                # Quality check
                is_good, reason = check_image_quality(img_path)
                
                if is_good:
                    plantdoc_images[standard_class].append(img_path)
                    stats['processed'] += 1
                    stats['mapped'] += 1
                else:
                    stats['errors'] += 1
    
    print(f"\n   ✅ PlantDoc Processing Complete:")
    print(f"      Class folders found: {stats['total_folders']}")
    print(f"      Total images: {stats['total_images']}")
    print(f"      Successfully processed: {stats['processed']}")
    print(f"      Quality filtered: {stats['errors']}")
    print(f"      Unmapped folders: {stats['unmapped']}")
    print(f"      Final classes: {len(plantdoc_images)}")
    
    if stats['unmapped_folders']:
        print(f"\n   ⚠️ Unmapped PlantDoc folders:")
        for folder in stats['unmapped_folders']:
            print(f"      - {folder}")
    
    # Show distribution
    print(f"\n   📊 PlantDoc Class Distribution:")
    for cls, imgs in sorted(plantdoc_images.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"      {cls}: {len(imgs)} images")
    
    return dict(plantdoc_images)

def process_plantvillage():
    """Process PlantVillage dataset"""
    print(f"\n{'='*80}")
    print(f"📊 PROCESSING PLANTVILLAGE DATASET")
    print(f"{'='*80}")
    
    plantvillage_images = defaultdict(list)
    stats = {'total': 0, 'processed': 0, 'errors': 0}
    
    class_dirs = [d for d in os.listdir(PLANTVILLAGE_TRAIN) if os.path.isdir(os.path.join(PLANTVILLAGE_TRAIN, d))]
    
    print(f"\n   Found {len(class_dirs)} class folders")
    
    for class_dir in tqdm(class_dirs, desc="   Processing classes"):
        class_path = os.path.join(PLANTVILLAGE_TRAIN, class_dir)
        
        for img_file in os.listdir(class_path):
            if not img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
            
            stats['total'] += 1
            img_path = os.path.join(class_path, img_file)
            
            is_good, reason = check_image_quality(img_path)
            if is_good:
                plantvillage_images[class_dir].append(img_path)
                stats['processed'] += 1
            else:
                stats['errors'] += 1
    
    print(f"\n   ✅ PlantVillage Processing Complete:")
    print(f"      Total images: {stats['total']}")
    print(f"      Quality approved: {stats['processed']}")
    print(f"      Filtered: {stats['errors']}")
    print(f"      Classes: {len(plantvillage_images)}")
    
    return dict(plantvillage_images)

def merge_datasets(plantdoc_images, plantvillage_images):
    """Merge datasets intelligently"""
    print(f"\n{'='*80}")
    print(f"🔀 MERGING DATASETS")
    print(f"{'='*80}")
    
    all_classes = set(plantdoc_images.keys()) | set(plantvillage_images.keys())
    
    print(f"\n   Total unique classes: {len(all_classes)}")
    
    merged = defaultdict(list)
    
    print(f"\n   Merge details:")
    for class_name in sorted(all_classes):
        pd_imgs = plantdoc_images.get(class_name, [])
        pv_imgs = plantvillage_images.get(class_name, [])
        
        # Add all PlantDoc (priority - better quality)
        merged[class_name].extend(pd_imgs)
        
        # Add PlantVillage to reach target
        target = 1800
        remaining = target - len(pd_imgs)
        
        if remaining > 0 and pv_imgs:
            if len(pv_imgs) > remaining:
                sampled = random.sample(pv_imgs, remaining)
            else:
                sampled = pv_imgs
            merged[class_name].extend(sampled)
        
        source = "BOTH" if (pd_imgs and pv_imgs) else ("PlantDoc" if pd_imgs else "PlantVillage")
        print(f"      {class_name}: {len(pd_imgs)} PD + {len(merged[class_name])-len(pd_imgs)} PV = {len(merged[class_name])} ({source})")
    
    return dict(merged)

def create_final_dataset(merged_images):
    """Create final train/val/test splits"""
    print(f"\n{'='*80}")
    print(f"📁 CREATING FINAL DATASET")
    print(f"{'='*80}")
    
    os.makedirs(f"{OUTPUT_DIR}/train", exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/valid", exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/test", exist_ok=True)
    
    final_stats = {
        'classes': {},
        'total_train': 0,
        'total_valid': 0,
        'total_test': 0
    }
    
    print(f"\n   Creating splits for {len(merged_images)} classes...")
    
    for class_name in tqdm(sorted(merged_images.keys()), desc="   Progress"):
        images = merged_images[class_name]
        
        # Create class directories
        os.makedirs(f"{OUTPUT_DIR}/train/{class_name}", exist_ok=True)
        os.makedirs(f"{OUTPUT_DIR}/valid/{class_name}", exist_ok=True)
        os.makedirs(f"{OUTPUT_DIR}/test/{class_name}", exist_ok=True)
        
        # Shuffle
        random.shuffle(images)
        
        # Split: 80% train, 10% val, 10% test
        n_train = int(0.8 * len(images))
        n_val = int(0.1 * len(images))
        
        train_imgs = images[:n_train]
        val_imgs = images[n_train:n_train + n_val]
        test_imgs = images[n_train + n_val:]
        
        # Copy files
        for i, img_path in enumerate(train_imgs):
            ext = Path(img_path).suffix
            dst = f"{OUTPUT_DIR}/train/{class_name}/{i:04d}{ext}"
            shutil.copy2(img_path, dst)
        
        for i, img_path in enumerate(val_imgs):
            ext = Path(img_path).suffix
            dst = f"{OUTPUT_DIR}/valid/{class_name}/{i:04d}{ext}"
            shutil.copy2(img_path, dst)
        
        for i, img_path in enumerate(test_imgs):
            ext = Path(img_path).suffix
            dst = f"{OUTPUT_DIR}/test/{class_name}/{i:04d}{ext}"
            shutil.copy2(img_path, dst)
        
        final_stats['classes'][class_name] = {
            'train': len(train_imgs),
            'valid': len(val_imgs),
            'test': len(test_imgs),
            'total': len(images)
        }
        final_stats['total_train'] += len(train_imgs)
        final_stats['total_valid'] += len(val_imgs)
        final_stats['total_test'] += len(test_imgs)
    
    # Save metadata
    with open(f"{OUTPUT_DIR}/dataset_info.json", 'w') as f:
        json.dump(final_stats, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"🎉 ULTIMATE DATASET COMPLETE!")
    print(f"{'='*80}")
    print(f"\n📊 Statistics:")
    print(f"   Classes: {len(final_stats['classes'])}")
    print(f"   Training: {final_stats['total_train']}")
    print(f"   Validation: {final_stats['total_valid']}")
    print(f"   Test: {final_stats['total_test']}")
    print(f"   TOTAL: {final_stats['total_train'] + final_stats['total_valid'] + final_stats['total_test']}")
    print(f"\n📁 Location: {os.path.abspath(OUTPUT_DIR)}/")

def main():
    random.seed(42)
    
    # Process both datasets
    plantdoc_images = process_plantdoc()
    
    if not plantdoc_images:
        print("\n⚠️ No PlantDoc images processed, using PlantVillage only")
    
    plantvillage_images = process_plantvillage()
    
    if not plantdoc_images and not plantvillage_images:
        print("\n❌ No datasets found!")
        return
    
    # Merge
    merged = merge_datasets(plantdoc_images, plantvillage_images)
    
    # Create final
    create_final_dataset(merged)
    
    print(f"\n{'='*80}")
    print(f"✅ READY FOR TRAINING!")
    print(f"{'='*80}")
    print(f"\nNext step:")
    print(f"   python train_ultimate.py")

if __name__ == "__main__":
    main()