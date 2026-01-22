"""
DocumentProcessor module for SentinAI.
Handles document analysis and information extraction using LayoutLM.
"""

import os
from typing import Optional

import torch
from PIL import Image
from transformers import pipeline
import easyocr


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
        # Initialize EasyOCR reader
        self.ocr_reader = easyocr.Reader(['en'], gpu=torch.cuda.is_available())
        self.supported_image_formats = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
        self.supported_pdf_format = ".pdf"
    
    def _extract_text_with_ocr(self, image: Image.Image) -> dict:
        """
        Extract text from image using EasyOCR with bounding boxes.
        
        Args:
            image: PIL Image object
            
        Returns:
            Dictionary with 'words' and 'boxes' for LayoutLM
        """
        try:
            import numpy as np
            img_array = np.array(image)
            ocr_results = self.ocr_reader.readtext(img_array)
            
            words = []
            boxes = []
            for (bbox, text, confidence) in ocr_results:
                # Convert bbox to LayoutLM format [x0, y0, x1, y1]
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                box = [min(x_coords), min(y_coords), max(x_coords), max(y_coords)]
                
                words.append(text)
                boxes.append(box)
            
            return {"words": words, "boxes": boxes}
        except Exception as e:
            return {"words": [], "boxes": []}

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
            
            # Poppler path for Windows
            poppler_path = None
            if os.name == 'nt':  # Windows
                backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                poppler_bin = os.path.join(backend_dir, "poppler", "poppler-24.08.0", "Library", "bin")
                if os.path.exists(poppler_bin):
                    poppler_path = poppler_bin
            
            images = convert_from_path(
                pdf_path,
                first_page=page_number + 1,
                last_page=page_number + 1,
                dpi=200,
                poppler_path=poppler_path
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

            # Extract text with OCR and provide normalized word_boxes to the pipeline
            ocr_data = self._extract_text_with_ocr(image)
            
            def _normalize_boxes(boxes, img_width: int, img_height: int):
                """Normalize absolute pixel boxes to 0-1000 scale required by LayoutLM."""
                normalized = []
                for box in boxes:
                    x0, y0, x1, y1 = box
                    # Avoid division by zero and clamp into [0, 1000]
                    nx0 = int(max(0, min(1000, (x0 / max(1, img_width)) * 1000)))
                    ny0 = int(max(0, min(1000, (y0 / max(1, img_height)) * 1000)))
                    nx1 = int(max(0, min(1000, (x1 / max(1, img_width)) * 1000)))
                    ny1 = int(max(0, min(1000, (y1 / max(1, img_height)) * 1000)))
                    normalized.append([nx0, ny0, nx1, ny1])
                return normalized

            if ocr_data["words"] and ocr_data["boxes"]:
                img_width, img_height = image.size
                normalized_boxes = _normalize_boxes(ocr_data["boxes"], img_width, img_height)
                word_boxes = list(zip(ocr_data["words"], normalized_boxes))
                result = self.pipeline(image, query, word_boxes=word_boxes)
            else:
                # Fallback: let the pipeline do its own OCR
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
