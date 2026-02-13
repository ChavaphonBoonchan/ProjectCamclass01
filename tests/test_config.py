"""
Test script to verify config save/load functionality
สคริปต์ทดสอบการบันทึกและโหลด config
"""

from face_common.config import DetectionConfig, load_config, save_config
from pathlib import Path
import json

print("=" * 60)
print("Config Save/Load Test")
print("=" * 60)

config_path = Path("detection_debug/config.example.json")

# 1. Load current config
print("\n[1] Loading current config...")
try:
    cfg = load_config(config_path)
    print(f"   OK - Config loaded from: {config_path}")
    print(f"   Current values:")
    print(f"     - provider: {cfg.provider}")
    print(f"     - threshold: {cfg.threshold}")
    print(f"     - min_face_size: {cfg.min_face_size}")
    print(f"     - resize_max: {cfg.resize_max}")
    print(f"     - send_interval_ms: {cfg.send_interval_ms}")
    print(f"     - camera_index: {cfg.camera_index}")
except Exception as e:
    print(f"   ERROR: {e}")
    exit(1)

# 2. Verify all fields
print("\n[2] Verifying all required fields...")
required_fields = [
    'camera_index', 'camera_id', 'width', 'height', 'fps_limit',
    'model_dir', 'provider', 'threshold', 'unknown_label', 'min_face_size',
    'send_mode', 'endpoint_http', 'endpoint_ws', 'send_interval_ms',
    'send_image', 'jpeg_quality', 'resize_max'
]

missing_fields = []
for field in required_fields:
    if not hasattr(cfg, field):
        missing_fields.append(field)
        print(f"   WARNING - Missing field: {field}")

if not missing_fields:
    print(f"   OK - All {len(required_fields)} required fields present")
else:
    print(f"   ERROR - Missing {len(missing_fields)} fields")

# 3. Test save
print("\n[3] Testing save functionality...")
test_config_path = Path("detection_debug/config.test.json")
try:
    save_config(cfg, test_config_path)
    print(f"   OK - Config saved to: {test_config_path}")
except Exception as e:
    print(f"   ERROR: {e}")
    exit(1)

# 4. Test load saved config
print("\n[4] Testing load of saved config...")
try:
    cfg2 = load_config(test_config_path)
    print(f"   OK - Config loaded from: {test_config_path}")
except Exception as e:
    print(f"   ERROR: {e}")
    exit(1)

# 5. Compare values
print("\n[5] Comparing original vs saved/loaded...")
differences = []
for field in required_fields:
    val1 = getattr(cfg, field, None)
    val2 = getattr(cfg2, field, None)
    if val1 != val2:
        differences.append((field, val1, val2))
        print(f"   DIFF - {field}: {val1} -> {val2}")

if not differences:
    print(f"   OK - All values match perfectly")
else:
    print(f"   WARNING - Found {len(differences)} differences")

# 6. Verify JSON format
print("\n[6] Verifying JSON format...")
try:
    with open(test_config_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"   OK - Valid JSON format")
    print(f"   Fields in JSON: {len(data)}")
    
    # Check for all required fields in JSON
    missing_in_json = []
    for field in required_fields:
        if field not in data:
            missing_in_json.append(field)
    
    if missing_in_json:
        print(f"   WARNING - Missing in JSON: {missing_in_json}")
    else:
        print(f"   OK - All required fields in JSON")
        
except Exception as e:
    print(f"   ERROR: {e}")

# 7. Clean up
print("\n[7] Cleaning up...")
try:
    test_config_path.unlink()
    print(f"   OK - Removed test file: {test_config_path}")
except Exception as e:
    print(f"   WARNING: {e}")

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

if not missing_fields and not differences:
    print("Status: PASS")
    print("Config save/load is working correctly!")
else:
    print("Status: FAIL")
    if missing_fields:
        print(f"  - Missing fields: {missing_fields}")
    if differences:
        print(f"  - Value differences: {len(differences)}")

print("=" * 60)
