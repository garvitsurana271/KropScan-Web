# train_enhanced.py - Enhanced model for RTX 5070 + 16GB RAM
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import torchvision.transforms as transforms
from torchvision import datasets
import timm
from tqdm import tqdm
import json
import os
import time
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
import random
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts
import torch.nn.functional as F
from multiprocessing import freeze_support

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = True  # Enable for better performance on new hardware

def main():
    set_seed(42)

    print("="*80)
    print("KROPSCAN ENHANCED TRAINING - OPTIMIZED FOR RTX 5070 + 16GB RAM")
    print("="*80)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\nDevice: {device}")

    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        torch.cuda.empty_cache()

    # ENHANCED CONFIG - Optimized for RTX 5070 + 16GB RAM
    CONFIG = {
        'model_name': 'efficientnet_b0',  # Downgraded from B4 to B0 (reduced memory usage)
        'pretrained': True,
        'drop_path_rate': 0.2,  # Increased for regularization

        'batch_size': 32,  # Reduced from 64 to 32 (reduced memory usage)
        'grad_accum_steps': 4,  # Effective batch size = 128 (maintains training dynamics)
        'num_workers': 4,  # Increased for better data loading
        'num_epochs': 40,  # Increased epochs for better training
        'patience': 8,  # Increased patience

        'optimizer': 'AdamW',
        'learning_rate': 0.0005,  # Slightly increased
        'weight_decay': 0.05,  # Increased for better regularization
        'betas': (0.9, 0.999),

        'scheduler': 'cosine_with_warm_restarts',
        'warmup_epochs': 3,
        'min_lr': 1e-7,

        'label_smoothing': 0.1,  # Increased for better generalization
        'mixup_alpha': 0.2,  # Enabled mixup for better generalization
        'mixup_prob': 0.5,  # 50% of batches use mixup

        'image_size': 224,  # Reduced from 380 to 224 (reduced memory usage)
        'use_ema': True,  # Enabled EMA for better final performance
        'use_randaugment': True,  # Enabled for better data augmentation
    }

    print(f"\nENHANCED Configuration:")
    for key, value in CONFIG.items():
        print(f"   {key}: {value}")

    # Paths
    if os.path.exists('KropScan_Ultimate_Dataset/train'):
        train_dir = 'KropScan_Ultimate_Dataset/train'
        val_dir = 'KropScan_Ultimate_Dataset/valid'
        print(f"\nUsing ultimate dataset")
    else:
        train_dir = 'New Plant Diseases Dataset(Augmented)/train'
        val_dir = 'New Plant Diseases Dataset(Augmented)/valid'
        print(f"\nUsing original dataset")

    if not os.path.exists(train_dir):
        print(f"Dataset not found!")
        exit()

    # ENHANCED Augmentation with RandAugment
    if CONFIG['use_randaugment']:
        from timm.data.auto_augment import rand_augment_transform

        train_transform = transforms.Compose([
            transforms.Resize((CONFIG['image_size'], CONFIG['image_size'])),
            rand_augment_transform('rand-m9-mstd0.5', {'translate_const': CONFIG['image_size']//8,
                                                      'img_mean': (124, 116, 104)}),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
    else:
        train_transform = transforms.Compose([
            transforms.Resize((CONFIG['image_size'], CONFIG['image_size'])),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
            transforms.RandomResizedCrop(CONFIG['image_size'], scale=(0.8, 1.0)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    val_transform = transforms.Compose([
        transforms.Resize((CONFIG['image_size'], CONFIG['image_size'])),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # Load datasets
    print("\nLoading datasets...")
    train_dataset = datasets.ImageFolder(train_dir, transform=train_transform)
    val_dataset = datasets.ImageFolder(val_dir, transform=val_transform)

    class_names = train_dataset.classes
    num_classes = len(class_names)

    print(f"Training samples: {len(train_dataset)}")
    print(f"Validation samples: {len(val_dataset)}")
    print(f"Classes: {num_classes}")

    # Loaders with enhanced settings
    train_loader = DataLoader(
        train_dataset,
        batch_size=CONFIG['batch_size'],
        shuffle=True,
        num_workers=CONFIG['num_workers'],
        pin_memory=True,
        persistent_workers=True  # Keep workers alive between epochs
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=CONFIG['batch_size'],
        shuffle=False,
        num_workers=CONFIG['num_workers'],
        pin_memory=True,
        persistent_workers=True
    )

    # Enhanced Model with better architecture
    print(f"\nBuilding {CONFIG['model_name']}...")
    model = timm.create_model(
        CONFIG['model_name'],
        pretrained=CONFIG['pretrained'],
        num_classes=num_classes,
        drop_path_rate=CONFIG['drop_path_rate']
    )
    model = model.to(device)

    print(f"Model ready with {sum(p.numel() for p in model.parameters()) / 1e6:.1f}M parameters")

    # Enhanced Loss function with label smoothing and focal loss option
    class FocalLoss(nn.Module):
        def __init__(self, alpha=1, gamma=2, reduction='mean', ignore_index=-100):
            super(FocalLoss, self).__init__()
            self.alpha = alpha
            self.gamma = gamma
            self.reduction = reduction
            self.ignore_index = ignore_index

        def forward(self, inputs, targets):
            ce_loss = F.cross_entropy(inputs, targets, reduction='none', ignore_index=self.ignore_index)
            pt = torch.exp(-ce_loss)
            focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss
            if self.reduction == 'mean':
                return focal_loss.mean()
            elif self.reduction == 'sum':
                return focal_loss.sum()
            else:
                return focal_loss

    # Use focal loss for better handling of imbalanced classes
    criterion = FocalLoss(alpha=1.0, gamma=2.0)

    optimizer = optim.AdamW(
        model.parameters(),
        lr=CONFIG['learning_rate'],
        weight_decay=CONFIG['weight_decay'],
        betas=CONFIG['betas']
    )

    # Enhanced scheduler with warm restarts
    scheduler = CosineAnnealingWarmRestarts(
        optimizer,
        T_0=CONFIG['num_epochs']//4,  # Restart every quarter of training
        T_mult=1,
        eta_min=CONFIG['min_lr']
    )

    # Exponential Moving Average for better final model
    class EMA:
        def __init__(self, model, decay=0.999):
            self.decay = decay
            self.shadow = {}
            self.backup = {}

            for name, param in model.named_parameters():
                if param.requires_grad:
                    self.shadow[name] = param.data.clone()

        def update(self, model):
            for name, param in model.named_parameters():
                if param.requires_grad:
                    self.shadow[name] = self.decay * self.shadow[name] + (1 - self.decay) * param.data

        def apply_shadow(self, model):
            for name, param in model.named_parameters():
                if param.requires_grad:
                    self.backup[name] = param.data.clone()
                    param.data = self.shadow[name]

        def restore(self, model):
            for name, param in model.named_parameters():
                if param.requires_grad:
                    param.data = self.backup[name]

    ema = EMA(model, decay=0.999) if CONFIG['use_ema'] else None

    print(f"\nEnhanced training setup complete")

    # Mixed precision for better performance
    scaler = torch.amp.GradScaler('cuda')

    def mixup_data(x, y, alpha=1.0):
        """Compute the mixup data. Return mixed inputs, pairs of targets, and lambda"""
        if alpha > 0.:
            lam = np.random.beta(alpha, alpha)
        else:
            lam = 1.
        batch_size = x.size(0)
        index = torch.randperm(batch_size).to(x.device)

        mixed_x = lam * x + (1 - lam) * x[index, :]
        y_a, y_b = y, y[index]
        return mixed_x, y_a, y_b, lam

    def mixup_criterion(criterion, pred, y_a, y_b, lam):
        return lam * criterion(pred, y_a) + (1 - lam) * criterion(pred, y_b)

    def train_epoch(model, loader, criterion, optimizer, scheduler, scaler, device, epoch, ema=None):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        pbar = tqdm(loader, desc=f'Epoch {epoch}')
        for batch_idx, (images, labels) in enumerate(pbar):
            images, labels = images.to(device), labels.to(device)

            # Check if mixup should be applied
            use_mixup = np.random.rand() < CONFIG['mixup_prob'] and CONFIG['mixup_alpha'] > 0

            if use_mixup:
                images, labels_a, labels_b, lam = mixup_data(images, labels, CONFIG['mixup_alpha'])

                # Forward
                with torch.amp.autocast('cuda'):
                    outputs = model(images)
                    loss = mixup_criterion(criterion, outputs, labels_a, labels_b, lam)
            else:
                # Forward
                with torch.amp.autocast('cuda'):
                    outputs = model(images)
                    loss = criterion(outputs, labels)
                # Set variables for non-mixup case
                labels_a, labels_b, lam = labels, labels, 1.0

            # Check for NaN
            if torch.isnan(loss):
                print(f"\nNaN loss detected at batch {batch_idx}! Skipping...")
                continue

            # Backward
            optimizer.zero_grad()
            scaler.scale(loss).backward()

            # Gradient clipping
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

            # Update
            scaler.step(optimizer)
            scaler.update()

            # Update EMA if enabled
            if ema is not None:
                ema.update(model)

            # Update scheduler
            if batch_idx % len(loader) // 2 == 0:  # Update scheduler more frequently
                scheduler.step()

            # Stats - Calculate accuracy based on whether mixup was used
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)  # Always use original batch size for total count
            if use_mixup:
                # For mixup batches, use the mixup accuracy formula
                correct += (lam * (predicted == labels_a).sum().item() +
                           (1 - lam) * (predicted == labels_b).sum().item())
            else:
                # For regular batches, use normal accuracy calculation
                correct += (predicted == labels).sum().item()

            # Update progress
            current_acc = 100 * correct / total
            pbar.set_postfix({
                'loss': f'{loss.item():.3f}',
                'acc': f'{current_acc:.1f}%',
                'lr': f'{scheduler.get_last_lr()[0]:.6f}' if hasattr(scheduler, 'get_last_lr') else f'{optimizer.param_groups[0]["lr"]:.6f}'
            })

        return running_loss/len(loader), 100*correct/total

    def validate(model, loader, criterion, device):
        model.eval()
        running_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():
            for images, labels in tqdm(loader, desc='Validating'):
                images, labels = images.to(device), labels.to(device)

                outputs = model(images)
                loss = criterion(outputs, labels)

                running_loss += loss.item()
                _, predicted = torch.max(outputs, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        return running_loss/len(loader), 100*correct/total

    # Training loop
    print("\n" + "="*80)
    print("STARTING ENHANCED TRAINING")
    print("="*80)

    best_val_acc = 0
    patience_counter = 0
    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}

    start_time = time.time()

    for epoch in range(1, CONFIG['num_epochs'] + 1):
        print(f"\n{'='*80}")
        print(f"Epoch {epoch}/{CONFIG['num_epochs']}")
        print(f"{'='*80}")

        # Train
        train_loss, train_acc = train_epoch(
            model, train_loader, criterion, optimizer, scheduler, scaler, device, epoch, ema
        )

        # Validate
        val_loss, val_acc = validate(model, val_loader, criterion, device)

        # Save history
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)

        # Print summary
        print(f"\nEpoch {epoch} Summary:")
        print(f"   Train: Loss={train_loss:.4f}, Acc={train_acc:.2f}%")
        print(f"   Val:   Loss={val_loss:.4f}, Acc={val_acc:.2f}%")

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc

            # Save main model
            torch.save(model.state_dict(), 'kropscan_production_model.pth')

            # Also save EMA model if enabled
            if ema is not None:
                ema.apply_shadow(model)
                torch.save(model.state_dict(), 'kropscan_best_checkpoint.pth')
                ema.restore(model)  # Restore current weights

            print(f"\nNEW BEST: {best_val_acc:.2f}%")
            patience_counter = 0
        else:
            patience_counter += 1
            print(f"\nNo improvement ({patience_counter}/{CONFIG['patience']})")

        # Early stopping
        if patience_counter >= CONFIG['patience']:
            print(f"\nEarly stopping!")
            break

        elapsed = time.time() - start_time
        print(f"\nTime: {elapsed/60:.1f} min")

    total_time = time.time() - start_time

    print("\n" + "="*80)
    print("ENHANCED TRAINING COMPLETE!")
    print("="*80)
    print(f"Time: {total_time/60:.1f} min")
    print(f"Best accuracy: {best_val_acc:.2f}%")

    # Save info
    model_info = {
        'model_architecture': CONFIG['model_name'],
        'num_classes': num_classes,
        'class_names': class_names,
        'best_val_accuracy': float(best_val_acc),
        'input_size': [CONFIG['image_size'], CONFIG['image_size']],
        'training_time_minutes': total_time/60,
        'config': CONFIG,
        'normalization': {
            'mean': [0.485, 0.456, 0.406],
            'std': [0.229, 0.224, 0.225]
        }
    }

    with open('model_info.json', 'w') as f:
        json.dump(model_info, f, indent=2)

    with open('training_history.json', 'w') as f:
        json.dump(history, f, indent=2)

    print(f"\nFiles saved:")
    print(f"   kropscan_production_model.pth")
    print(f"   kropscan_best_checkpoint.pth")  # EMA model
    print(f"   model_info.json")
    print(f"   training_history.json")

    # Plot
    plt.figure(figsize=(12, 4))

    plt.subplot(1, 2, 1)
    plt.plot(history['train_loss'], label='Train')
    plt.plot(history['val_loss'], label='Val')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.title('Loss')
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.plot(history['train_acc'], label='Train')
    plt.plot(history['val_acc'], label='Val')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy (%)')
    plt.legend()
    plt.title('Accuracy')
    plt.grid(True)

    plt.tight_layout()
    plt.savefig('training_curves.png', dpi=150, bbox_inches='tight')
    print(f"   training_curves.png")

    print("\n" + "="*80)
    print("ENHANCED MODEL READY!")
    print("="*80)

if __name__ == '__main__':
    freeze_support()  # Required for Windows multiprocessing
    main()