"""
TicketClassifier module for SentinAI.
Handles support ticket classification using scikit-learn ML pipeline.
"""

import os
from typing import Dict, List, Optional, Tuple

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline


class TicketClassifier:
    """
    Production-ready ticket classifier for categorizing support tickets
    using TF-IDF vectorization and Random Forest classification.
    """

    MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models")
    MODEL_FILENAME = "ticket_classifier.joblib"

    def __init__(self):
        """
        Initialize the TicketClassifier.
        Attempts to load existing model or creates a new untrained pipeline.
        """
        self.categories: List[str] = ["Billing", "Technical", "Account"]
        self.pipeline: Optional[Pipeline] = None
        self._ensure_models_dir()
        self._load_or_initialize()

    def _ensure_models_dir(self) -> None:
        """Ensure the models directory exists."""
        os.makedirs(self.MODELS_DIR, exist_ok=True)

    def _get_model_path(self) -> str:
        """Get the full path to the model file."""
        return os.path.join(self.MODELS_DIR, self.MODEL_FILENAME)

    def _load_or_initialize(self) -> None:
        """Load existing model or initialize a new pipeline."""
        model_path = self._get_model_path()
        if os.path.exists(model_path):
            try:
                self.pipeline = joblib.load(model_path)
            except Exception:
                self._initialize_pipeline()
        else:
            self._initialize_pipeline()

    def _initialize_pipeline(self) -> None:
        """Initialize a new sklearn pipeline."""
        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                stop_words="english"
            )),
            ("classifier", RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            ))
        ])

    def train_default_model(self) -> Dict[str, str]:
        """
        Train the classifier on a default dummy dataset of support categories.
        
        Returns:
            Dictionary with status and message.
        """
        training_data: List[str] = [
            "I was charged twice for my subscription",
            "Why is my bill higher this month",
            "I need a refund for the overcharge",
            "Can you explain the charges on my invoice",
            "Payment failed but money was deducted",
            "I want to cancel and get my money back",
            "The application keeps crashing",
            "I cannot connect to the server",
            "Error message when trying to upload files",
            "The system is running very slow",
            "Feature X is not working as expected",
            "How do I configure the API settings",
            "I forgot my password and cannot reset it",
            "How do I change my email address",
            "I want to delete my account",
            "Cannot update my profile information",
            "How do I enable two-factor authentication",
            "I need to change my subscription plan",
        ]

        labels: List[str] = [
            "Billing", "Billing", "Billing", "Billing", "Billing", "Billing",
            "Technical", "Technical", "Technical", "Technical", "Technical", "Technical",
            "Account", "Account", "Account", "Account", "Account", "Account",
        ]

        try:
            self._initialize_pipeline()
            self.pipeline.fit(training_data, labels)
            self.save_model()
            return {
                "status": "success",
                "message": f"Model trained on {len(training_data)} samples with {len(self.categories)} categories"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Training failed: {str(e)}"
            }

    def predict(self, text: str) -> Dict[str, any]:
        """
        Predict the category of a support ticket.
        
        Args:
            text: The ticket text to classify.
            
        Returns:
            Dictionary containing:
                - status: 'success' or 'error'
                - category: Predicted category (on success)
                - probability: Confidence score (on success)
                - message: Error message (on error)
        """
        if not text or not text.strip():
            return {
                "status": "error",
                "message": "Input text cannot be empty"
            }

        try:
            if not hasattr(self.pipeline, "classes_"):
                return {
                    "status": "error",
                    "message": "Model not trained. Call train_default_model() first."
                }

            prediction = self.pipeline.predict([text])[0]
            probabilities = self.pipeline.predict_proba([text])[0]
            max_probability = float(max(probabilities))

            return {
                "status": "success",
                "category": prediction,
                "probability": round(max_probability, 4)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Prediction failed: {str(e)}"
            }

    def save_model(self) -> Dict[str, str]:
        """
        Save the trained model to disk.
        
        Returns:
            Dictionary with status and message.
        """
        try:
            model_path = self._get_model_path()
            joblib.dump(self.pipeline, model_path)
            return {
                "status": "success",
                "message": f"Model saved to {model_path}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to save model: {str(e)}"
            }

    def load_model(self) -> Dict[str, str]:
        """
        Load a trained model from disk.
        
        Returns:
            Dictionary with status and message.
        """
        try:
            model_path = self._get_model_path()
            if not os.path.exists(model_path):
                return {
                    "status": "error",
                    "message": f"No model found at {model_path}"
                }
            self.pipeline = joblib.load(model_path)
            return {
                "status": "success",
                "message": f"Model loaded from {model_path}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to load model: {str(e)}"
            }
