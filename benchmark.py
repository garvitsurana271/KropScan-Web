# benchmark.py - Test and benchmark the enhanced KropScan AI
import time
import torch
import numpy as np
from PIL import Image
import io
import os
from ai_engine import KropScanAI

def create_test_image(size=(380, 380)):
    """Create a test image for benchmarking"""
    # Create a realistic test image
    image = Image.new('RGB', size, color='green')
    # Add some patterns to make it look like a leaf
    pixels = image.load()
    for i in range(size[0]):
        for j in range(size[1]):
            if (i - size[0]//2)**2 + (j - size[1]//2)**2 < (size[0]//3)**2:
                # Center area - make it more leaf-like
                pixels[i, j] = (34, 139, 34)  # Forest green
            else:
                # Edge area - add some variation
                pixels[i, j] = (20, 100, 20)
    
    # Add some "disease spots"
    for i in range(50, 100):
        for j in range(50, 100):
            if (i - 75)**2 + (j - 75)**2 < 25**2:
                pixels[i, j] = (139, 69, 19)  # Brown spot
    
    return image

def benchmark_model():
    """Run comprehensive benchmarks on the enhanced model"""
    print("="*80)
    print("🚀 KROPSCAN ENHANCED MODEL BENCHMARK")
    print("="*80)
    
    # Initialize AI engine
    print("\n🔧 Loading Enhanced AI Engine...")
    ai = KropScanAI(
        model_path='kropscan_production_model.pth',
        config_path='model_info.json',
        use_tta=True,
        tta_size=5
    )
    
    if not ai.model_loaded:
        print("❌ Model not loaded. Please run training first.")
        return
    
    print(f"✅ Model loaded: {ai.config['model_architecture']}")
    print(f"✅ Input size: {ai.input_size}x{ai.input_size}")
    print(f"✅ Classes: {ai.num_classes}")
    
    # Create test image
    test_image = create_test_image((ai.input_size, ai.input_size))
    
    # Convert to bytes for testing
    img_byte_arr = io.BytesIO()
    test_image.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    
    print(f"\n📊 Starting benchmarks...")
    
    # Benchmark 1: Single prediction speed
    print("\n⏱️ BENCHMARK 1: Single Prediction Speed")
    times = []
    for i in range(10):
        start_time = time.time()
        result = ai.predict(img_byte_arr)
        end_time = time.time()
        prediction_time = end_time - start_time
        times.append(prediction_time)
        print(f"   Run {i+1}: {prediction_time:.3f}s - {result[0]} (confidence: {result[1]:.3f})")
    
    avg_time = np.mean(times)
    std_time = np.std(times)
    print(f"   Average: {avg_time:.3f}s ± {std_time:.3f}s")
    print(f"   Speed: {1/avg_time:.2f} predictions/second")
    
    # Benchmark 2: Memory usage
    print("\n💾 BENCHMARK 2: Memory Usage")
    if torch.cuda.is_available():
        initial_memory = torch.cuda.memory_allocated()
        print(f"   Initial GPU memory: {initial_memory / 1024**2:.1f} MB")
        
        # Run a few predictions
        for _ in range(5):
            ai.predict(img_byte_arr)
        
        peak_memory = torch.cuda.max_memory_allocated()
        current_memory = torch.cuda.memory_allocated()
        print(f"   Peak GPU memory: {peak_memory / 1024**2:.1f} MB")
        print(f"   Current GPU memory: {current_memory / 1024**2:.1f} MB")
        print(f"   Memory used by model: {(peak_memory - initial_memory) / 1024**2:.1f} MB")
    
    # Benchmark 3: Accuracy consistency
    print("\n🎯 BENCHMARK 3: Prediction Consistency")
    predictions = []
    confidences = []
    
    for i in range(10):
        result = ai.predict(img_byte_arr)
        predictions.append(result[0])
        confidences.append(result[1])
        print(f"   Run {i+1}: {result[0]} (confidence: {result[1]:.3f})")
    
    # Analyze consistency
    unique_predictions = list(set(predictions))
    consistency = predictions.count(predictions[0]) / len(predictions)
    avg_confidence = np.mean(confidences)
    std_confidence = np.std(confidences)
    
    print(f"   Consistency: {consistency:.2f}")
    print(f"   Unique predictions: {len(unique_predictions)}")
    print(f"   Average confidence: {avg_confidence:.3f} ± {std_confidence:.3f}")
    
    # Benchmark 4: TTA effectiveness
    print("\n🔍 BENCHMARK 4: TTA Effectiveness")
    # Test with TTA
    ai_with_tta = KropScanAI(use_tta=True)
    ai_without_tta = KropScanAI(use_tta=False)
    
    if ai_with_tta.model_loaded and ai_without_tta.model_loaded:
        # Run same image with and without TTA
        start_time = time.time()
        result_with_tta = ai_with_tta.predict(img_byte_arr)
        time_with_tta = time.time() - start_time
        
        start_time = time.time()
        result_without_tta = ai_without_tta.predict(img_byte_arr)
        time_without_tta = time.time() - start_time
        
        print(f"   With TTA: {result_with_tta[0]} (confidence: {result_with_tta[1]:.3f}) in {time_with_tta:.3f}s")
        print(f"   Without TTA: {result_without_tta[0]} (confidence: {result_without_tta[1]:.3f}) in {time_without_tta:.3f}s")
        print(f"   TTA Speed Factor: {time_with_tta/time_without_tta:.2f}x slower")
        print(f"   Confidence Difference: {abs(result_with_tta[1] - result_without_tta[1]):.3f}")
    
    print("\n" + "="*80)
    print("✅ BENCHMARK COMPLETE")
    print("="*80)
    
    # Summary
    print(f"\n📋 ENHANCED MODEL SUMMARY:")
    print(f"   • Architecture: {ai.config['model_architecture']}")
    print(f"   • Input Resolution: {ai.input_size}x{ai.input_size}")
    print(f"   • Average Speed: {1/avg_time:.2f} predictions/second")
    print(f"   • Average Confidence: {avg_confidence:.3f}")
    print(f"   • Consistency: {consistency:.2f}")
    print(f"   • TTA Augmentations: {len(ai.tta_augmenter.augmentations)}")
    
    if torch.cuda.is_available():
        print(f"   • Peak GPU Memory: {peak_memory / 1024**2:.1f} MB")

if __name__ == "__main__":
    benchmark_model()