# -*- coding: utf-8 -*-
"""
สคริปต์ทดสอบการตรวจจับ GPU และ CUDA
Test script for GPU and CUDA detection
"""
import sys
import io

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("GPU Detection Test")
print("=" * 60)

# 1. ตรวจสอบ ONNX Runtime
print("\n[1] Checking ONNX Runtime:")
try:
    import onnxruntime as ort
    print(f"   OK - onnxruntime version: {ort.__version__}")
    
    providers = ort.get_available_providers()
    print(f"   Available providers: {providers}")
    
    if 'CUDAExecutionProvider' in providers:
        print("   OK - CUDA Provider: Available")
    else:
        print("   WARNING - CUDA Provider: Not available")
        print("   You may need to install onnxruntime-gpu")
        
except ImportError:
    print("   ERROR - onnxruntime not found")
    print("   Run: pip install onnxruntime")

# 2. ตรวจสอบ NVIDIA GPU
print("\n[2] Checking NVIDIA GPU:")
try:
    import subprocess
    result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, encoding='utf-8')
    if result.returncode == 0:
        print("   OK - NVIDIA GPU: Detected")
        # แสดงข้อมูล GPU
        lines = result.stdout.split('\n')
        for line in lines:
            if 'NVIDIA' in line or 'RTX' in line or 'GTX' in line or 'GeForce' in line:
                print(f"   Info: {line.strip()}")
    else:
        print("   WARNING - NVIDIA GPU: Not detected")
except FileNotFoundError:
    print("   WARNING - nvidia-smi: Command not found")
    print("   You may not have NVIDIA GPU or driver installed")

# 3. ตรวจสอบ CUDA
print("\n[3] Checking CUDA Toolkit:")
try:
    import subprocess
    result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True, encoding='utf-8')
    if result.returncode == 0:
        print("   OK - CUDA Toolkit: Installed")
        version_line = [line for line in result.stdout.split('\n') if 'release' in line.lower()]
        if version_line:
            print(f"   Info: {version_line[0].strip()}")
    else:
        print("   WARNING - CUDA Toolkit: Not found")
except FileNotFoundError:
    print("   WARNING - CUDA Toolkit: Not installed")
    print("   Download: https://developer.nvidia.com/cuda-downloads")

# 4. ทดสอบ Face Engine
print("\n[4] Testing Face Engine:")
try:
    from face_common.face_engine import get_available_providers, is_gpu_available, auto_select_provider
    
    providers = get_available_providers()
    print(f"   Available providers: {providers}")
    
    gpu_available = is_gpu_available()
    print(f"   GPU available: {gpu_available}")
    
    selected = auto_select_provider()
    print(f"   Auto-selected provider: {selected}")
    
    if selected == "CUDAExecutionProvider":
        print("   OK - System will use GPU!")
    else:
        print("   INFO - System will use CPU")
        
except Exception as e:
    print(f"   ERROR: {e}")

# 5. ตรวจสอบ GPUtil (optional)
print("\n[5] Checking GPU Monitoring Tools:")
try:
    import GPUtil
    gpus = GPUtil.getGPUs()
    if gpus:
        print(f"   OK - Found {len(gpus)} GPU(s)")
        for i, gpu in enumerate(gpus):
            print(f"   GPU {i}: {gpu.name}")
            print(f"      Memory: {gpu.memoryUsed:.0f}/{gpu.memoryTotal:.0f} MB")
            print(f"      Utilization: {gpu.load*100:.1f}%")
    else:
        print("   WARNING - No GPU found")
except ImportError:
    print("   WARNING - GPUtil: Not installed")
    print("   Run: pip install gputil")
except Exception as e:
    print(f"   WARNING - Error: {e}")

# สรุป
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

try:
    import onnxruntime as ort
    providers = ort.get_available_providers()
    
    if 'CUDAExecutionProvider' in providers:
        print("Status: GPU Ready")
        print("System will run on GPU automatically")
    else:
        print("Status: CPU Only")
        print("\nHow to enable GPU:")
        print("  1. Check if you have NVIDIA GPU: nvidia-smi")
        print("  2. Install CUDA Toolkit (if not installed)")
        print("  3. Install onnxruntime-gpu:")
        print("     pip uninstall onnxruntime -y")
        print("     pip install onnxruntime-gpu")
        print("  4. Run this script again to verify")
except:
    print("ERROR - Cannot check status")

print("=" * 60)
