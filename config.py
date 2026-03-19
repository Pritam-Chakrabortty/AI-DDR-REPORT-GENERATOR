#!/usr/bin/env python3
"""
Configuration and Error Handling Module
Centralized configuration and error handling for the DDR Generator
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants for report generator
BULLET_CHAR = '&bull;'
LINE_BREAK = '<br/>'

@dataclass
class DDRConfig:
    """Configuration class for DDR Generator"""
    # API Configuration
    gemini_api_key: str = os.getenv('GEMINI_API_KEY', 'AIzaSyB1Gd6bSr_QC3ohiOseP1fQgkCuv5UAB8Q')
    
    # File Paths
    output_dir: str = os.getenv('OUTPUT_FOLDER', 'output')
    log_file: str = os.getenv('LOG_FILE', 'output/ddr_generator.log')
    
    # Processing Limits
    max_images_per_section: int = 5
    max_text_length: int = 50000  # Maximum characters to send to AI
    
    # Report Settings
    report_title: str = "DETAILED DIAGNOSTIC REPORT"
    report_subtitle: str = "AI-Powered Property Analysis"
    
    # PDF Settings
    page_size: str = "A4"
    margins: Dict[str, float] = None
    
    # Web Application Settings
    flask_secret_key: str = os.getenv('FLASK_SECRET_KEY', 'ddr_generator_secret_key_2024_secure_random')
    upload_folder: str = os.getenv('UPLOAD_FOLDER', 'uploads')
    max_content_length: int = int(os.getenv('MAX_CONTENT_LENGTH', '52428800'))  # 50MB
    debug: bool = os.getenv('DEBUG', 'True').lower() == 'true'
    
    def __post_init__(self):
        if self.margins is None:
            self.margins = {
                'top': 72,
                'bottom': 18,
                'left': 72,
                'right': 72
            }

class DDRException(Exception):
    """Base exception class for DDR Generator"""
    pass

class PDFProcessingError(DDRException):
    """Exception raised during PDF processing"""
    pass

class AIProcessingError(DDRException):
    """Exception raised during AI processing"""
    pass

class ReportGenerationError(DDRException):
    """Exception raised during report generation"""
    pass

class ConfigurationError(DDRException):
    """Exception raised for configuration issues"""
    pass

class ErrorHandler:
    """Centralized error handling and logging"""
    
    def __init__(self, config: DDRConfig):
        self.config = config
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger('DDR_Generator')
        logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatters
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        try:
            os.makedirs(os.path.dirname(self.config.log_file), exist_ok=True)
            file_handler = logging.FileHandler(self.config.log_file)
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not setup file logging: {e}")
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def handle_pdf_error(self, error: Exception, pdf_path: str) -> None:
        """Handle PDF processing errors"""
        error_msg = f"PDF processing error for {pdf_path}: {str(error)}"
        self.logger.error(error_msg)
        raise PDFProcessingError(error_msg) from error
    
    def handle_ai_error(self, error: Exception) -> None:
        """Handle AI processing errors"""
        error_msg = f"AI processing error: {str(error)}"
        self.logger.error(error_msg)
        raise AIProcessingError(error_msg) from error
    
    def handle_report_error(self, error: Exception, output_path: str) -> None:
        """Handle report generation errors"""
        error_msg = f"Report generation error for {output_path}: {str(error)}"
        self.logger.error(error_msg)
        raise ReportGenerationError(error_msg) from error
    
    def handle_config_error(self, error: Exception) -> None:
        """Handle configuration errors"""
        error_msg = f"Configuration error: {str(error)}"
        self.logger.error(error_msg)
        raise ConfigurationError(error_msg) from error
    
    def log_info(self, message: str) -> None:
        """Log info message"""
        self.logger.info(message)
    
    def log_warning(self, message: str) -> None:
        """Log warning message"""
        self.logger.warning(message)
    
    def log_error(self, message: str) -> None:
        """Log error message"""
        self.logger.error(message)
    
    def log_debug(self, message: str) -> None:
        """Log debug message"""
        self.logger.debug(message)

def validate_environment(config: DDRConfig) -> bool:
    """Validate the environment and configuration"""
    try:
        # Check if output directory can be created
        output_path = Path(config.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Check if log file can be written
        log_path = Path(config.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Validate API key format (basic check)
        if not config.gemini_api_key or len(config.gemini_api_key) < 10:
            raise ConfigurationError("Invalid Gemini API key")
        
        return True
        
    except Exception as e:
        raise ConfigurationError(f"Environment validation failed: {str(e)}")

def safe_file_operation(operation, file_path: str, error_handler: ErrorHandler):
    """Safely perform file operations with error handling"""
    try:
        return operation()
    except FileNotFoundError:
        error_handler.handle_pdf_error(Exception(f"File not found: {file_path}"), file_path)
    except PermissionError:
        error_handler.handle_pdf_error(Exception(f"Permission denied: {file_path}"), file_path)
    except Exception as e:
        error_handler.handle_pdf_error(e, file_path)

def cleanup_temp_files(config: DDRConfig, error_handler: ErrorHandler) -> None:
    """Clean up temporary files and directories"""
    try:
        output_dir = Path(config.output_dir)
        if output_dir.exists():
            # Clean up old log files (keep only last 5)
            log_dir = Path(config.log_file).parent
            if log_dir.exists():
                log_files = sorted(log_dir.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)
                for old_log in log_files[5:]:
                    old_log.unlink()
                    error_handler.log_info(f"Cleaned up old log file: {old_log}")
                    
    except Exception as e:
        error_handler.log_warning(f"Cleanup failed: {str(e)}")

# Global configuration instance
config = DDRConfig()
error_handler = ErrorHandler(config)
