#!/usr/bin/env python3
"""
Script de Test Simple - nuts_vision
Simple test script for testing component detection with a single photo.

Usage:
    python test_simple.py --model path/to/model.pt --image path/to/photo.jpg
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from detect import ComponentDetector
    import cv2
except ImportError as e:
    print("❌ Erreur d'importation / Import error:")
    print(f"   {e}")
    print("\n💡 Installez les dépendances / Install dependencies:")
    print("   pip install -r requirements.txt")
    sys.exit(1)


def print_banner():
    """Print welcome banner."""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║              nuts_vision - Test Simple                       ║")
    print("║          Détection de Composants Électroniques              ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()


def test_image(model_path: str, image_path: str, conf_threshold: float = 0.25):
    """
    Test component detection on a single image.
    
    Args:
        model_path: Path to trained YOLO model
        image_path: Path to image to test
        conf_threshold: Confidence threshold for detections
    """
    print("🔍 Configuration:")
    print(f"   Modèle / Model: {model_path}")
    print(f"   Image: {image_path}")
    print(f"   Seuil de confiance / Confidence: {conf_threshold}")
    print()
    
    # Check if files exist
    if not Path(model_path).exists():
        print(f"❌ Erreur: Modèle introuvable / Model not found: {model_path}")
        print()
        print("💡 Placez smd_comp.pt dans le répertoire racine du projet / Place smd_comp.pt in the project root directory.")
        return False
    
    if not Path(image_path).exists():
        print(f"❌ Erreur: Image introuvable / Image not found: {image_path}")
        return False
    
    print("="*60)
    print("🚀 Début de la détection / Starting detection...")
    print("="*60)
    print()
    
    try:
        # Initialize detector
        detector = ComponentDetector(model_path, conf_threshold=conf_threshold)
        
        # Run detection
        detections = detector.detect_components(
            image_path,
            save_visualization=True,
            output_dir="outputs/results"
        )
        
        # Display results
        print("✅ Détection terminée / Detection complete!")
        print()
        print("="*60)
        print(f"📊 Résultats / Results: {len(detections)} composants détectés")
        print("="*60)
        print()
        
        if not detections:
            print("⚠️  Aucun composant détecté / No components detected")
            print()
            print("💡 Essayez / Try:")
            print("   - Réduire le seuil de confiance: --conf 0.15")
            print("   - Utiliser une image de meilleure qualité")
            print("   - Vérifier que l'image contient des composants visibles")
            return True
        
        # Count by type
        component_counts = {}
        for det in detections:
            comp_type = det['class_name']
            component_counts[comp_type] = component_counts.get(comp_type, 0) + 1
        
        # Display summary
        print("📋 Composants détectés par type:")
        for i, (comp_type, count) in enumerate(sorted(component_counts.items()), 1):
            print(f"   {i}. {comp_type}: {count}")
        print()
        
        # Display top 10 detections
        print("🔝 Top 10 détections (par confiance):")
        sorted_dets = sorted(detections, key=lambda x: x['confidence'], reverse=True)[:10]
        for i, det in enumerate(sorted_dets, 1):
            print(f"   {i}. {det['class_name']}: {det['confidence']:.2%}")
        print()
        
        # Show output location
        output_image = Path("outputs/results") / f"{Path(image_path).stem}_detected.jpg"
        print("="*60)
        print("💾 Fichiers de sortie / Output files:")
        print("="*60)
        print(f"   📸 Image annotée / Annotated image:")
        print(f"      {output_image}")
        print(f"   📄 Détections JSON:")
        print(f"      outputs/results/detections.json")
        print()
        
        # Try to display image info
        img = cv2.imread(str(image_path))
        if img is not None:
            h, w = img.shape[:2]
            print(f"ℹ️  Info image: {w}x{h} pixels")
        
        print()
        print("="*60)
        print("✨ Test terminé avec succès / Test completed successfully!")
        print("="*60)
        print()
        print("💡 Étapes suivantes / Next steps:")
        print("   1. Ouvrez l'image annotée pour voir les détections")
        print("      Open the annotated image to see detections")
        print()
        print("   2. Pour une analyse complète avec le pipeline:")
        print("      For full analysis with pipeline:")
        print("      python src/pipeline.py --model smd_comp.pt --image", image_path)
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur / Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Script de test simple pour la détection de composants / Simple test script for component detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples / Examples:
  # Test avec smd_comp.pt / Test with smd_comp.pt
  python test_simple.py --model smd_comp.pt --image ma_carte.jpg
  
  # Avec seuil de confiance ajusté / With adjusted confidence threshold
  python test_simple.py --model smd_comp.pt --image photo.jpg --conf 0.3
  
  # Afficher l'aide / Show help
  python test_simple.py --help
        """
    )
    
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Chemin vers le modèle YOLO entraîné / Path to trained YOLO model"
    )
    parser.add_argument(
        "--image",
        type=str,
        required=True,
        help="Chemin vers l'image à tester / Path to image to test"
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Seuil de confiance (0.0-1.0, défaut: 0.25) / Confidence threshold (default: 0.25)"
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Run test
    success = test_image(args.model, args.image, args.conf)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
