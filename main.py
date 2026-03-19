#!/usr/bin/env python3
"""
AI-powered Detailed Diagnostic Report (DDR) Generator
Main execution script that orchestrates the entire DDR generation process
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

from pdf_extractor import PDFExtractor
from ai_processor import AIProcessor
from report_generator import ReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('output/ddr_generator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def get_pdf_files():
    """
    Get PDF file paths from user input
    Returns tuple of (inspection_report_path, thermal_report_path)
    """
    print("\n" + "="*60)
    print("AI-POWERED DETAILED DIAGNOSTIC REPORT (DDR) GENERATOR")
    print("="*60)
    
    while True:
        inspection_path = input("\nEnter path to Inspection Report PDF: ").strip()
        if os.path.exists(inspection_path) and inspection_path.lower().endswith('.pdf'):
            break
        print("❌ Invalid file path or not a PDF. Please try again.")
    
    while True:
        thermal_path = input("\nEnter path to Thermal Report PDF: ").strip()
        if os.path.exists(thermal_path) and thermal_path.lower().endswith('.pdf'):
            break
        print("❌ Invalid file path or not a PDF. Please try again.")
    
    return inspection_path, thermal_path

def main():
    """
    Main execution function
    """
    try:
        # Get input files
        inspection_path, thermal_path = get_pdf_files()
        
        # Create output directory
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Initialize components
        logger.info("Initializing DDR Generator components...")
        pdf_extractor = PDFExtractor()
        ai_processor = AIProcessor()
        report_generator = ReportGenerator()
        
        # Step 1: Extract data from PDFs
        logger.info("Extracting data from Inspection Report...")
        inspection_data = pdf_extractor.extract_from_pdf(inspection_path, "inspection")
        
        logger.info("Extracting data from Thermal Report...")
        thermal_data = pdf_extractor.extract_from_pdf(thermal_path, "thermal")
        
        # Step 2: Process with AI
        logger.info("Processing data with AI to generate DDR...")
        ddr_content = ai_processor.generate_ddr(inspection_data, thermal_data)
        
        # Step 3: Generate report
        logger.info("Generating final DDR report...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"DDR_Report_{timestamp}.pdf"
        
        report_generator.create_ddr_pdf(
            ddr_content=ddr_content,
            inspection_images=inspection_data['images'],
            thermal_images=thermal_data['images'],
            output_path=str(output_path)
        )
        
        # Display results
        print("\n" + "="*60)
        print("✅ DDR GENERATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"📄 Report saved to: {output_path}")
        print(f"🖼️  Images extracted: {len(inspection_data['images']) + len(thermal_data['images'])}")
        print(f"📝 Log file: output/ddr_generator.log")
        
        # Display DDR content
        print("\n" + "="*60)
        print("GENERATED DDR REPORT CONTENT:")
        print("="*60)
        print(ddr_content)
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        print("\n\n⚠️  Process interrupted by user")
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
        print("📝 Check output/ddr_generator.log for detailed error information")
        sys.exit(1)

if __name__ == "__main__":
    main()
