#!/usr/bin/env python3
"""
PDF Extractor Module
Handles text and image extraction from PDF documents using PyMuPDF (fitz)
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

class PDFExtractor:
    """
    Extracts text and images from PDF documents
    """
    
    def __init__(self):
        """Initialize the PDF extractor"""
        self.supported_image_formats = ['png', 'jpg', 'jpeg', 'bmp', 'tiff']
        
    def extract_from_pdf(self, pdf_path: str, report_type: str) -> Dict:
        """
        Extract text and images from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            report_type: Type of report ('inspection' or 'thermal')
            
        Returns:
            Dictionary containing extracted text and images
        """
        try:
            logger.info(f"Extracting from {report_type} report: {pdf_path}")
            
            # Create output directory for images
            images_dir = Path("output") / f"{report_type}_images"
            images_dir.mkdir(parents=True, exist_ok=True)
            
            extracted_data = {
                'text': '',
                'images': [],
                'metadata': {}
            }
            
            # Open PDF document
            doc = fitz.open(pdf_path)
            
            # Extract metadata
            extracted_data['metadata'] = {
                'page_count': doc.page_count,
                'title': doc.metadata.get('title', 'Unknown'),
                'author': doc.metadata.get('author', 'Unknown'),
                'creator': doc.metadata.get('creator', 'Unknown')
            }
            
            # Process each page
            for page_num in range(doc.page_count):
                page = doc[page_num]
                
                # Extract text from page
                page_text = page.get_text()
                if page_text.strip():
                    extracted_data['text'] += f"\n--- Page {page_num + 1} ---\n"
                    extracted_data['text'] += page_text + "\n"
                
                # Extract images from page
                page_images = self._extract_images_from_page(
                    page, page_num, images_dir, report_type
                )
                extracted_data['images'].extend(page_images)
            
            doc.close()
            
            logger.info(f"Extracted {len(extracted_data['images'])} images from {report_type} report")
            logger.info(f"Extracted {len(extracted_data['text'])} characters of text from {report_type} report")
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error extracting from PDF {pdf_path}: {str(e)}")
            raise
    
    def _extract_images_from_page(self, page, page_num: int, images_dir: Path, report_type: str) -> List[Dict]:
        """
        Extract images from a single PDF page
        
        Args:
            page: PyMuPDF page object
            page_num: Page number (0-indexed)
            images_dir: Directory to save images
            report_type: Type of report for naming
            
        Returns:
            List of dictionaries containing image information
        """
        images = []
        
        try:
            # Get image list from page
            image_list = page.get_images(full=True)
            
            for img_index, img_info in enumerate(image_list):
                try:
                    # Get image data
                    xref = img_info[0]
                    base_image = page.parent.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Generate filename
                    image_filename = f"{report_type}_page_{page_num + 1}_img_{img_index + 1}.{image_ext}"
                    image_path = images_dir / image_filename
                    
                    # Save image
                    with open(image_path, "wb") as img_file:
                        img_file.write(image_bytes)
                    
                    # Store image information
                    image_info = {
                        'filename': image_filename,
                        'path': str(image_path),
                        'page': page_num + 1,
                        'index': img_index + 1,
                        'format': image_ext,
                        'size': len(image_bytes)
                    }
                    
                    images.append(image_info)
                    logger.debug(f"Extracted image: {image_filename}")
                    
                except Exception as e:
                    logger.warning(f"Failed to extract image {img_index} from page {page_num + 1}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.warning(f"Error processing images on page {page_num + 1}: {str(e)}")
        
        return images
    
    def validate_pdf(self, pdf_path: str) -> bool:
        """
        Validate if the file is a readable PDF
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            True if valid PDF, False otherwise
        """
        try:
            if not os.path.exists(pdf_path):
                logger.error(f"File does not exist: {pdf_path}")
                return False
            
            if not pdf_path.lower().endswith('.pdf'):
                logger.error(f"File is not a PDF: {pdf_path}")
                return False
            
            # Try to open the PDF
            doc = fitz.open(pdf_path)
            doc.close()
            
            return True
            
        except Exception as e:
            logger.error(f"PDF validation failed for {pdf_path}: {str(e)}")
            return False
    
    def get_pdf_info(self, pdf_path: str) -> Dict:
        """
        Get basic information about a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing PDF information
        """
        try:
            doc = fitz.open(pdf_path)
            
            info = {
                'page_count': doc.page_count,
                'metadata': doc.metadata,
                'file_size': os.path.getsize(pdf_path),
                'is_encrypted': doc.is_encrypted,
                'is_pdf': True
            }
            
            doc.close()
            return info
            
        except Exception as e:
            logger.error(f"Error getting PDF info for {pdf_path}: {str(e)}")
            return {
                'page_count': 0,
                'metadata': {},
                'file_size': 0,
                'is_encrypted': False,
                'is_pdf': False,
                'error': str(e)
            }
