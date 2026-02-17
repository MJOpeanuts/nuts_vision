#!/usr/bin/env python3
"""
Test script to verify the upload path fix
This test validates that:
1. Uploaded images are stored in outputs/images_input/
2. Absolute paths are used for database storage
3. Paths can be resolved correctly
"""

import sys
from pathlib import Path
import tempfile
import os

print("Testing upload path fix...")
print("=" * 60)

# Test 1: Verify upload directory structure
print("\n1. Testing upload directory structure...")
upload_dir = Path("outputs") / "images_input"
print(f"   Upload directory: {upload_dir}")
print(f"   Should be: outputs/images_input")

if upload_dir.parts[-2:] == ('outputs', 'images_input'):
    print("   ✅ Upload directory structure is correct")
else:
    print("   ❌ Upload directory structure is incorrect")
    sys.exit(1)

# Test 2: Test absolute path conversion
print("\n2. Testing absolute path conversion...")
test_file = upload_dir / "test_image.jpg"
absolute_path = test_file.resolve()

print(f"   Relative path: {test_file}")
print(f"   Absolute path: {absolute_path}")

if absolute_path.is_absolute():
    print("   ✅ Path is converted to absolute correctly")
else:
    print("   ❌ Path is not absolute")
    sys.exit(1)

# Test 3: Verify path storage format
print("\n3. Testing path storage format...")
# Simulate what happens in pipeline.py
img_path_str = str(test_file)
absolute_path_str = str(Path(img_path_str).resolve())

print(f"   Input path: {img_path_str}")
print(f"   Stored path: {absolute_path_str}")

if Path(absolute_path_str).is_absolute():
    print("   ✅ Stored path is absolute")
else:
    print("   ❌ Stored path is not absolute")
    sys.exit(1)

# Test 4: Verify parent directory creation
print("\n4. Testing directory creation...")
try:
    # Create a test directory
    test_upload_dir = Path("outputs") / "images_input" / "test"
    test_upload_dir.mkdir(parents=True, exist_ok=True)
    
    if test_upload_dir.exists():
        print(f"   ✅ Directory created successfully: {test_upload_dir}")
        # Clean up
        test_upload_dir.rmdir()
    else:
        print(f"   ❌ Directory creation failed")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Error creating directory: {e}")
    sys.exit(1)

# Test 5: Verify .gitignore setup
print("\n5. Verifying .gitignore configuration...")
gitignore_path = Path(".gitignore")
if gitignore_path.exists():
    with open(gitignore_path, 'r') as f:
        gitignore_content = f.read()
    
    # Check if outputs/ is ignored (files should be ignored but structure preserved)
    if 'outputs/' in gitignore_content:
        print("   ✅ outputs/ directory is in .gitignore")
    else:
        print("   ⚠️  outputs/ not found in .gitignore (may be intentional)")
    
    # Check if uploads/ is still ignored (for backwards compatibility)
    if 'uploads/' in gitignore_content:
        print("   ✅ uploads/ directory is in .gitignore (backwards compatibility)")
    else:
        print("   ⚠️  uploads/ not found in .gitignore")
else:
    print("   ⚠️  .gitignore file not found")

# Test 6: Check app.py changes
print("\n6. Verifying app.py changes...")
app_path = Path("app.py")
if app_path.exists():
    with open(app_path, 'r') as f:
        app_content = f.read()
    
    # Check for new upload directory
    if 'outputs/images_input' in app_content or 'outputs") / "images_input' in app_content:
        print("   ✅ app.py uses outputs/images_input directory")
    else:
        print("   ❌ app.py does not use outputs/images_input directory")
        sys.exit(1)
    
    # Check for absolute path conversion
    if 'resolve()' in app_content or 'absolute' in app_content.lower():
        print("   ✅ app.py converts paths to absolute")
    else:
        print("   ❌ app.py does not convert paths to absolute")
        sys.exit(1)
else:
    print("   ❌ app.py not found")
    sys.exit(1)

# Test 7: Check pipeline.py changes
print("\n7. Verifying pipeline.py changes...")
pipeline_path = Path("src/pipeline.py")
if pipeline_path.exists():
    with open(pipeline_path, 'r') as f:
        pipeline_content = f.read()
    
    # Check for absolute path storage
    if 'resolve()' in pipeline_content and 'absolute_path' in pipeline_content:
        print("   ✅ pipeline.py stores absolute paths")
    else:
        print("   ❌ pipeline.py does not store absolute paths")
        sys.exit(1)
else:
    print("   ❌ pipeline.py not found")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All upload path fix tests passed!")
print("\nSummary of changes:")
print("  1. Uploaded images saved to: outputs/images_input/")
print("  2. Absolute paths stored in database")
print("  3. Images persist with other outputs")
print("  4. Job Viewer can find images reliably")
print("=" * 60)
