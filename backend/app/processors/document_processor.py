"""
DocumentProcessor module for SentinAI.
Handles document analysis and information extraction using LayoutLM.
"""

import os
from typing import Optional

import torch
from PIL import Image
from transformers import pipeline


class DocumentProcessor:
    """
    High-performance document processor for extracting information
    from documents using LayoutLM with automatic hardware optimization.
    """

    def __init__(self, model_name: str = "impira/layoutlm-document-qa"):
        """
        Initialize the DocumentProcessor with LayoutLM pipeline.
        
        Args:
            model_name: Name of the HuggingFace model to use for document QA.
                       Defaults to 'impira/layoutlm-document-qa'.
        """
        self.device = 0 if torch.cuda.is_available() else -1
        self.pipeline = pipeline(
            "document-question-answering",
            model=model_name,
            device=self.device
        )
        self.supported_image_formats = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
        self.supported_pdf_format = ".pdf"

    def _convert_pdf_to_image(self, pdf_path: str, page_number: int = 0) -> Optional[Image.Image]:
        """
        Convert a PDF page to an image for processing by the vision model.
        
        Args:
            pdf_path: Path to the PDF file.
            page_number: Page number to convert (0-indexed). Defaults to 0.
            
        Returns:
            PIL Image object of the converted page, or None if conversion fails.
            
        Raises:
            ImportError: If pdf2image is not installed.
        """
        try:
            from pdf2image import convert_from_path
            
            images = convert_from_path(
                pdf_path,
                first_page=page_number + 1,
                last_page=page_number + 1,
                dpi=200
            )
            
            if images:
                return images[0]
            return None
            
        except ImportError:
            raise ImportError(
                "pdf2image is required for PDF processing. "
                "Install it with: pip install pdf2image"
            )

    def extract_info(self, file_path: str, query: str) -> dict:
        """
        Extract information from a document based on a natural language query.
        
        Args:
            file_path: Path to the document file (PDF or image).
            query: Natural language question to ask about the document.
            
        Returns:
            Dictionary containing:
                - status: 'success' or 'error'
                - answer: Extracted answer (on success)
                - confidence_score: Model confidence score (on success)
                - message: Error message (on error)
        """
        if not os.path.exists(file_path):
            return {
                "status": "error",
                "message": f"File not found: {file_path}"
            }

        file_extension = os.path.splitext(file_path)[1].lower()

        try:
            image: Optional[Image.Image] = None

            if file_extension == self.supported_pdf_format:
                image = self._convert_pdf_to_image(file_path)
                if image is None:
                    return {
                        "status": "error",
                        "message": "Failed to convert PDF to image"
                    }

            elif file_extension in self.supported_image_formats:
                image = Image.open(file_path)

            else:
                return {
                    "status": "error",
                    "message": f"Unsupported file format: {file_extension}. "
                              f"Supported formats: {self.supported_image_formats | {self.supported_pdf_format}}"
                }

            result = self.pipeline(image, query)

            if result and len(result) > 0:
                return {
                    "status": "success",
                    "answer": result[0].get("answer", ""),
                    "confidence_score": result[0].get("score", 0.0)
                }

            return {
                "status": "error",
                "message": "No answer could be extracted from the document"
            }

        except ImportError as e:
            return {
                "status": "error",
                "message": str(e)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Document processing failed: {str(e)}"
            }
