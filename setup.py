#!/usr/bin/env python3
"""
Setup script to help configure the nuts_vision project.
"""

import sys
import subprocess
from pathlib import Path


def check_dataset():
    """Check if dataset directories exist."""
    required_dirs = ['train/images', 'valid/images', 'test/images']
    missing_dirs = []
    
    print("Checking dataset structure...")
    for dir_path in required_dirs:
        full_path = Path(dir_path)
        if full_path.exists():
            # Count images
            images = list(full_path.glob('*.jpg')) + list(full_path.glob('*.png'))
            print(f"  ✓ {dir_path} ({len(images)} images)")
        else:
            print(f"  ✗ {dir_path} - NOT FOUND")
            missing_dirs.append(dir_path)
    
    return len(missing_dirs) == 0


def create_directories():
    """Create necessary output directories."""
    dirs = [
        'outputs',
        'outputs/results',
        'outputs/cropped_components',
        'outputs/visualizations',
        'models'
    ]
    
    print("\nCreating output directories...")
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {dir_path}")


def check_data_yaml():
    """Check if data.yaml is properly configured."""
    data_yaml = Path('data.yaml')
    
    print("\nChecking data.yaml configuration...")
    if not data_yaml.exists():
        print("  ✗ data.yaml not found")
        return False
    
    # Read and check content
    with open(data_yaml, 'r') as f:
        content = f.read()
    
    required_keys = ['train:', 'val:', 'test:', 'nc:', 'names:']
    missing = [key for key in required_keys if key not in content]
    
    if missing:
        print(f"  ✗ Missing required keys: {', '.join(missing)}")
        return False
    
    print("  ✓ data.yaml looks good")
    return True


def install_dependencies():
    """Install Python dependencies."""
    print("\nInstalling Python dependencies...")
    print("This may take a few minutes...")
    
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
            check=True
        )
        print("  ✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("  ✗ Failed to install dependencies")
        return False


def main():
    print("="*60)
    print("nuts_vision - Setup Script")
    print("="*60 + "\n")
    
    # Create output directories
    create_directories()
    
    # Check data.yaml
    yaml_ok = check_data_yaml()
    
    # Check dataset
    print()
    dataset_ok = check_dataset()
    
    # Summary
    print("\n" + "="*60)
    print("SETUP SUMMARY")
    print("="*60)
    
    if not yaml_ok:
        print("\n⚠ data.yaml needs to be configured")
        print("\nPlease ensure data.yaml points to your dataset directories.")
    
    if not dataset_ok:
        print("\n⚠ Dataset not found or incomplete")
        print("\nOptions:")
        print("  1. Download the CompDetect dataset from Roboflow")
        print("     Visit: https://app.roboflow.com/peanuts-q9amc/compdetect-f6vw8/3")
        print("  2. Use your own dataset in YOLO format")
        print("\nExtract the dataset to this directory and update data.yaml")
    else:
        print("\n✓ Dataset found and configured")
    
    # Offer to install dependencies
    if yaml_ok and dataset_ok:
        print("\n" + "="*60)
        response = input("\nInstall Python dependencies now? (y/n): ")
        if response.lower() == 'y':
            install_dependencies()
    
    print("\n" + "="*60)
    print("Next steps:")
    print("="*60)
    print("\n1. Check dependencies:")
    print("   python check_dependencies.py")
    print("\n2. Train the model:")
    print("   python src/train.py --data data.yaml --epochs 100")
    print("\n3. Process images:")
    print("   python src/pipeline.py --model <model_path> --image <image_path>")
    print("\nSee QUICKSTART.md for detailed instructions.")
    print()


if __name__ == "__main__":
    main()
