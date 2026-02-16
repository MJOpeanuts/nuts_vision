#!/usr/bin/env python3
"""
YOLO Model Training Script for Electronic Component Detection
Trains a YOLOv8 model on the CompDetect dataset for detecting electronic components.
"""

import argparse
from pathlib import Path
from ultralytics import YOLO


def train_model(
    data_yaml: str = "data.yaml",
    model_size: str = "n",
    epochs: int = 100,
    imgsz: int = 640,
    batch: int = 16,
    name: str = "component_detector",
    device: str = "0"
):
    """
    Train a YOLO model for component detection.
    
    Args:
        data_yaml: Path to data.yaml configuration file
        model_size: YOLO model size (n, s, m, l, x)
        epochs: Number of training epochs
        imgsz: Image size for training
        batch: Batch size
        name: Name for the training run
        device: Device to use (cuda device id or 'cpu')
    """
    # Initialize YOLO model
    model_name = f"yolov8{model_size}.pt"
    print(f"Loading {model_name} model...")
    model = YOLO(model_name)
    
    # Train the model
    print(f"Starting training for {epochs} epochs...")
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        name=name,
        device=device,
        patience=50,  # Early stopping patience
        save=True,
        save_period=10,  # Save checkpoint every 10 epochs
        plots=True,
        verbose=True
    )
    
    # Validate the model
    print("\nValidating model...")
    metrics = model.val()
    
    # Print training results
    print("\n" + "="*50)
    print("Training Complete!")
    print("="*50)
    print(f"Best model saved to: runs/detect/{name}/weights/best.pt")
    print(f"mAP50: {metrics.box.map50:.4f}")
    print(f"mAP50-95: {metrics.box.map:.4f}")
    
    return model, results


def main():
    parser = argparse.ArgumentParser(description="Train YOLO model for component detection")
    parser.add_argument(
        "--data", 
        type=str, 
        default="data.yaml",
        help="Path to data.yaml file"
    )
    parser.add_argument(
        "--model-size", 
        type=str, 
        default="n",
        choices=["n", "s", "m", "l", "x"],
        help="YOLO model size (n=nano, s=small, m=medium, l=large, x=xlarge)"
    )
    parser.add_argument(
        "--epochs", 
        type=int, 
        default=100,
        help="Number of training epochs"
    )
    parser.add_argument(
        "--imgsz", 
        type=int, 
        default=640,
        help="Image size for training"
    )
    parser.add_argument(
        "--batch", 
        type=int, 
        default=16,
        help="Batch size"
    )
    parser.add_argument(
        "--name", 
        type=str, 
        default="component_detector",
        help="Name for the training run"
    )
    parser.add_argument(
        "--device", 
        type=str, 
        default="0",
        help="Device to use (cuda device id or 'cpu')"
    )
    
    args = parser.parse_args()
    
    # Train the model
    train_model(
        data_yaml=args.data,
        model_size=args.model_size,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        name=args.name,
        device=args.device
    )


if __name__ == "__main__":
    main()
