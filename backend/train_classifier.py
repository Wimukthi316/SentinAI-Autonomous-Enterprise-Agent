"""
Training script for the SentinAI Ticket Classifier.
Trains the ML model and saves it to the models directory.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.models.ticket_classifier import TicketClassifier
    
    print("=" * 60)
    print("SentinAI Ticket Classifier - Training Script")
    print("=" * 60)
    print()
    
    # Initialize the classifier
    print("Initializing TicketClassifier...")
    classifier = TicketClassifier()
    
    # Train the model
    print("Training model on default dataset...")
    result = classifier.train_default_model()
    
    if result["status"] == "success":
        print()
        print("✓ Training completed successfully!")
        print(f"  {result['message']}")
        print()
        
        # Get the model path
        model_path = classifier._get_model_path()
        print(f"✓ Model saved to: {model_path}")
        print()
        
        # Verify the file exists
        if os.path.exists(model_path):
            file_size = os.path.getsize(model_path)
            print(f"  File size: {file_size:,} bytes")
            print(f"  Categories: {', '.join(classifier.categories)}")
        else:
            print("  Warning: Model file not found after training!")
        
        print()
        print("=" * 60)
        print("Training complete! The model is ready to use.")
        print("=" * 60)
    else:
        print()
        print("✗ Training failed!")
        print(f"  Error: {result['message']}")
        sys.exit(1)

except ImportError as e:
    print()
    print("✗ Import Error!")
    print(f"  Could not import TicketClassifier: {e}")
    print()
    print("  Make sure you are in the backend/ directory and all dependencies are installed.")
    print("  Run: pip install -r requirements.txt")
    sys.exit(1)

except Exception as e:
    print()
    print("✗ Unexpected Error!")
    print(f"  {type(e).__name__}: {e}")
    print()
    import traceback
    traceback.print_exc()
    sys.exit(1)
