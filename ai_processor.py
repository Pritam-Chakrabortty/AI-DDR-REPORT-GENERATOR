#!/usr/bin/env python3
"""
AI Processor Module
Handles AI processing using Google Gemini API for DDR generation
"""

import logging
import google.generativeai as genai
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class AIProcessor:
    """
    Processes extracted PDF data using Google Gemini AI to generate DDR reports
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI processor with Gemini API
        
        Args:
            api_key: Google Gemini API key (if None, will use environment variable)
        """
        from config import config
        self.api_key = api_key or config.gemini_api_key
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("Gemini AI model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {str(e)}")
            raise
    
    def generate_ddr(self, inspection_data: Dict, thermal_data: Dict) -> str:
        """
        Generate Detailed Diagnostic Report using AI
        
        Args:
            inspection_data: Extracted data from inspection report
            thermal_data: Extracted data from thermal report
            
        Returns:
            Generated DDR report as formatted string
        """
        try:
            # Combine text from both reports
            combined_text = self._prepare_combined_text(inspection_data, thermal_data)
            
            # Generate the DDR using AI
            prompt = self._create_ddr_prompt(combined_text)
            
            logger.info("Sending request to Gemini AI for DDR generation...")
            response = self.model.generate_content(prompt)
            
            if response.text:
                ddr_content = response.text.strip()
                logger.info("DDR generated successfully")
                return ddr_content
            else:
                logger.error("Empty response from Gemini AI")
                raise Exception("Empty response from AI model")
                
        except Exception as e:
            logger.error(f"Error generating DDR: {str(e)}")
            raise
    
    def _prepare_combined_text(self, inspection_data: Dict, thermal_data: Dict) -> str:
        """
        Prepare combined text from both reports for AI processing
        
        Args:
            inspection_data: Data from inspection report
            thermal_data: Data from thermal report
            
        Returns:
            Combined text string
        """
        combined_text = """
=== DETAILED DIAGNOSTIC REPORT (DDR) GENERATION ===
Combined data from Inspection Report and Thermal Report

"""
        
        # Add inspection report data
        combined_text += f"""
{'='*60}
INSPECTION REPORT DATA
{'='*60}

Pages: {inspection_data.get('metadata', {}).get('page_count', 'Unknown')}
Images Extracted: {len(inspection_data.get('images', []))}

INSPECTION REPORT TEXT:
{inspection_data.get('text', 'No text extracted')}

"""
        
        # Add thermal report data
        combined_text += f"""
{'='*60}
THERMAL REPORT DATA
{'='*60}

Pages: {thermal_data.get('metadata', {}).get('page_count', 'Unknown')}
Images Extracted: {len(thermal_data.get('images', []))}

THERMAL REPORT TEXT:
{thermal_data.get('text', 'No text extracted')}

"""
        
        # Add image information
        combined_text += f"""
{'='*60}
IMAGE INFORMATION
{'='*60}

Inspection Report Images:
"""
        for img in inspection_data.get('images', []):
            combined_text += f"- Page {img.get('page', '?')}: {img.get('filename', 'Unknown')}\n"
        
        combined_text += "\nThermal Report Images:\n"
        for img in thermal_data.get('images', []):
            combined_text += f"- Page {img.get('page', '?')}: {img.get('filename', 'Unknown')}\n"
        
        return combined_text
    
    def _create_ddr_prompt(self, combined_text: str) -> str:
        """
        Create the prompt for DDR generation
        
        Args:
            combined_text: Combined text from both reports
            
        Returns:
            Complete prompt for AI processing
        """
        prompt = f"""
You are an expert building inspector and thermal imaging analyst creating a premium Detailed Diagnostic Report (DDR). Generate a sophisticated, professional report that impresses clients with its clarity and thoroughness.

IMPORTANT INSTRUCTIONS:
1. DO NOT hallucinate or add fake data that is not present in the source documents
2. If information is missing, explicitly write "Not Available"
3. If data conflicts between reports, clearly mention the conflict
4. Avoid duplicate points - be concise and clear
5. Use sophisticated, professional language that builds confidence
6. Base your analysis ONLY on the provided text and image information
7. Create an elegant, well-structured report with clear visual hierarchy
8. STRICTLY FORBIDDEN: Do not use markdown characters like #, *, -, >, or bullet points.
9. OUTPUT FORMAT: Write in clear, flowing paragraphs only.

ANALYZE THE FOLLOWING DATA:
{combined_text}

GENERATE A PREMIUM DDR REPORT WITH THE FOLLOWING EXACT SECTIONS:

1. PROPERTY ISSUE SUMMARY
   - Begin with a compelling executive summary
   - Use professional, confident language
   - Present findings in clear, impactful statements
   - Focus on the most critical issues first

2. AREA-WISE OBSERVATIONS
   - Organize by location with clear headings
   - Use descriptive, professional language
   - Include specific measurements and details when available
   - Present observations in logical order

3. PROBABLE ROOT CAUSE
   - Provide expert-level analysis
   - Use technical but accessible language
   - Explain the "why" behind each issue
   - Demonstrate deep understanding of building science

4. SEVERITY ASSESSMENT
   - Provide clear severity rating (Low/Medium/High/Critical)
   - Include detailed, evidence-based reasoning
   - Explain potential impacts and risks
   - Use professional assessment language

5. RECOMMENDED ACTIONS
   - Prioritize actions with clear urgency levels
   - Provide specific, actionable recommendations
   - Include estimated timelines when possible
   - Suggest qualified professionals for each task

6. ADDITIONAL NOTES
   - Include valuable insights and observations
   - Mention relevant building codes or standards
   - Provide context for findings
   - Add any expert recommendations

7. MISSING OR UNCLEAR INFORMATION
   - Clearly identify information gaps
   - Explain why additional data would be valuable
   - Suggest methods to obtain missing information
   - Be transparent about limitations

FORMAT REQUIREMENTS:
- Use elegant, professional formatting throughout
- Create clear visual hierarchy with proper spacing
- Use sophisticated vocabulary and sentence structure
- Write in confident, authoritative tone
- Include transition phrases for smooth flow
- Use proper paragraph structure with topic sentences
- DO NOT use bullet points, asterisks, hashes, or casual formatting symbols
- DO NOT use markdown headers (like ## or ###)
- Make every section impressive and client-ready

Remember: This is a premium report that should demonstrate expertise and build client confidence. Be thorough, professional, and impressive while only using information actually present in the provided reports.
"""
        
        return prompt
    
    def test_api_connection(self) -> bool:
        """
        Test the connection to Gemini API
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            test_prompt = "Respond with 'API connection successful' if you can read this."
            response = self.model.generate_content(test_prompt)
            
            if response.text and "successful" in response.text.lower():
                logger.info("Gemini API connection test successful")
                return True
            else:
                logger.error("Unexpected response from API test")
                return False
                
        except Exception as e:
            logger.error(f"API connection test failed: {str(e)}")
            return False
    
    def get_model_info(self) -> Dict:
        """
        Get information about the AI model being used
        
        Returns:
            Dictionary containing model information
        """
        try:
            model_info = {
                'model_name': 'gemini-2.5-flash',
                'api_provider': 'Google Gemini',
                'status': 'active' if self.test_api_connection() else 'inactive'
            }
            return model_info
        except Exception as e:
            logger.error(f"Error getting model info: {str(e)}")
            return {
                'model_name': 'gemini-2.5-flash',
                'api_provider': 'Google Gemini',
                'status': 'error',
                'error': str(e)
            }
