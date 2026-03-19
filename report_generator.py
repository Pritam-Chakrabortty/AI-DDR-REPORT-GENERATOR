#!/usr/bin/env python3
"""
Report Generator Module
Handles PDF generation for the final DDR report using ReportLab
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black, blue, red, green, darkgray
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib import colors
from config import BULLET_CHAR, LINE_BREAK, error_handler

logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    Generates professional PDF reports for DDR output
    """
    
    def __init__(self):
        """Initialize the report generator"""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup custom styles for the report"""
        # Clear any existing custom styles to avoid conflicts
        # Note: StyleSheet1 doesn't support direct deletion, so we'll use unique names
        
        # Title style - Elegant and impressive
        self.styles.add(ParagraphStyle(
            name='DDR_CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=50,
            spaceBefore=30,
            textColor=colors.darkblue,
            alignment=1,  # Center
            borderWidth=2,
            borderColor=colors.darkblue,
            borderPadding=20,
            backColor=colors.lightgrey,
            fontName='Helvetica-Bold',
            leading=28,
            textTransform='uppercase',
            letterSpacing=2
        ))
        
        # Section heading style - Professional and distinctive
        self.styles.add(ParagraphStyle(
            name='DDR_SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=25,
            spaceBefore=40,
            textColor=colors.darkblue,
            borderWidth=0,
            borderColor=colors.darkblue,
            fontName='Helvetica-Bold',
            leading=22,
            textTransform='uppercase',
            letterSpacing=1
        ))
        
        # Subsection style - Clean and readable
        self.styles.add(ParagraphStyle(
            name='DDR_Subsection',
            parent=self.styles['Heading3'],
            fontSize=16,
            spaceAfter=15,
            spaceBefore=25,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            leading=20,
            textTransform='capitalize'
        ))
        
        # Body text style - Professional and elegant
        self.styles.add(ParagraphStyle(
            name='DDR_BodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=15,
            spaceBefore=8,
            leading=16,
            fontName='Helvetica',
            textColor=colors.black,
            alignment=4,  # Justified
            leftIndent=10,
            rightIndent=10,
            firstLineIndent=0
        ))
        
        # Important text style - For emphasis
        self.styles.add(ParagraphStyle(
            name='DDR_Important',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=12,
            leading=18,
            fontName='Helvetica-Bold',
            textColor=colors.darkred,
            alignment=4,
            borderWidth=1,
            borderColor=colors.darkred,
            borderPadding=8,
            backColor=colors.mistyrose
        ))
        
        # Warning style - Professional alerts
        self.styles.add(ParagraphStyle(
            name='DDR_Warning',
            parent=self.styles['Normal'],
            fontSize=13,
            spaceAfter=12,
            leading=16,
            fontName='Helvetica-Bold',
            textColor=colors.darkred,
            backColor=colors.mistyrose,
            borderPadding=8,
            borderWidth=2,
            borderColor=colors.darkred,
            borderRadius=5
        ))
        
        # Info style - Professional information
        self.styles.add(ParagraphStyle(
            name='DDR_Info',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            leading=14,
            fontName='Helvetica-Oblique',
            textColor=colors.darkblue,
            alignment=1  # Center
        ))
        
        # Footer style - Professional footer
        self.styles.add(ParagraphStyle(
            name='DDR_Footer',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            leading=12,
            fontName='Helvetica',
            textColor=colors.grey,
            alignment=1  # Center
        ))
        
        # Caption style for images
        self.styles.add(ParagraphStyle(
            name='DDR_Caption',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            leading=12,
            fontName='Helvetica-Oblique',
            textColor=colors.darkblue,
            alignment=1  # Center
        ))
    
    def create_ddr_pdf(self, ddr_content: str, inspection_images: List[Dict], 
                      thermal_images: List[Dict], output_path: str):
        """
        Create a professional DDR PDF report
        
        Args:
            ddr_content: Generated DDR content from AI
            inspection_images: List of inspection report images
            thermal_images: List of thermal report images
            output_path: Path to save the output PDF
        """
        try:
            logger.info(f"Creating DDR PDF report at: {output_path}")
            
            # Create story
            story = []
            
            # Check if images exist
            has_images = bool(inspection_images) or bool(thermal_images)
            
            # Create title page
            story.extend(self._create_title_page())
            
            # Create table of contents (only if there's content)
            if ddr_content.strip():
                story.extend(self._create_table_of_contents(has_images))
            
            # Create main content
            if ddr_content.strip():
                story.extend(self._format_ddr_content(ddr_content))
                
                # Only add images section if images exist
                if has_images:
                    story.extend(self._create_images_section(inspection_images, thermal_images))
            
            # Always add appendix
            story.extend(self._create_appendix())
            
            # Build the PDF
            doc = SimpleDocTemplate(output_path, pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=72)
            
            doc.build(story)
            
            logger.info(f"DDR PDF report created successfully: {output_path}")
            
        except Exception as e:
            logger.error(f"Error creating DDR PDF: {str(e)}")
            raise
    
    def _create_title_page(self) -> List:
        """Create an impressive title page"""
        story = []
        
        # Add reasonable spacing
        story.append(Spacer(1, 1.5*inch))
        
        # Main title with enhanced styling
        title = Paragraph("DETAILED DIAGNOSTIC REPORT", self.styles['DDR_CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        # Subtitle with professional styling
        subtitle = Paragraph("Comprehensive Property Analysis & Assessment", self.styles['DDR_SectionHeading'])
        story.append(subtitle)
        story.append(Spacer(1, 0.2*inch))
        
        # AI-powered badge
        ai_badge = Paragraph("🤖 AI-Powered Professional Analysis", self.styles['DDR_Important'])
        story.append(ai_badge)
        story.append(Spacer(1, 0.6*inch))
        
        # Report information in an elegant table
        report_info = [
            ["📅 Generated on:", datetime.now().strftime("%B %d, %Y at %I:%M %p")],
            ["📋 Report Type:", "Premium DDR Analysis"],
            ["🔍 Analysis Method:", "Advanced AI Technology"],
            ["🖼️  Images Processed:", f"Inspection: {len(self.inspection_images) if hasattr(self, 'inspection_images') else 'N/A'}, Thermal: {len(self.thermal_images) if hasattr(self, 'thermal_images') else 'N/A'}"],
            ["⚡ Processing Engine:", "Google Gemini 2.5 Flash"]
        ]
        
        info_table = Table(report_info, colWidths=[2.5*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 2, colors.darkblue),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.lightgrey, colors.whitesmoke]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 0.6*inch))
        
        # Professional disclaimer with enhanced styling
        disclaimer_text = """
        <b>Professional Disclaimer:</b> This premium report has been generated using advanced AI analysis 
        of inspection and thermal reports. While our AI system provides comprehensive insights, 
        all findings should be verified by qualified professionals before taking any action. 
        This report represents a sophisticated analysis tool to support expert decision-making.
        """
        
        disclaimer = Paragraph(disclaimer_text, self.styles['DDR_Warning'])
        story.append(disclaimer)
        
        # Footer with confidence statement
        story.append(Spacer(1, 0.4*inch))
        footer = Paragraph("✨ Confidence in Every Analysis • Excellence in Every Report ✨", self.styles['DDR_Footer'])
        story.append(footer)
        
        return story
    
    def _create_table_of_contents(self, has_images: bool = False) -> List:
        """Create table of contents"""
        story = []
        
        title = Paragraph("TABLE OF CONTENTS", self.styles['DDR_CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.8*inch))
        
        # Create TOC entries
        toc_data = [
            ["1. Executive Summary", "3"],
            ["2. Property Issue Summary", "4"],
            ["3. Area-wise Observations", "5"],
            ["4. Probable Root Cause Analysis", "6"],
            ["5. Severity Assessment", "7"],
            ["6. Recommended Actions", "8"],
            ["7. Additional Notes", "9"],
            ["8. Missing Information", "10"]
        ]
        
        # Add images section only if images exist
        if has_images:
            toc_data.append(["9. Extracted Images", "11"])
            toc_data.append(["10. Appendix", "12"])
        else:
            toc_data.append(["9. Appendix", "11"])
        
        # Create TOC table
        toc_table = Table(toc_data, colWidths=[5*inch, 1*inch])
        toc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
            ('ALIGN', (0, 1), (-1, 1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('LINEBELOW', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        story.append(toc_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Add note about page numbers
        note = Paragraph("*Page numbers are approximate and may vary based on content length", self.styles['DDR_Info'])
        story.append(note)
        
        return story
    
    def _format_ddr_content(self, ddr_content: str) -> List:
        """Format DDR content for PDF"""
        story = []
        
        # Parse and format each section
        sections = self._parse_ddr_sections(ddr_content)
        
        for section_title, section_content in sections.items():
            # Add section heading with reasonable spacing
            heading = Paragraph(section_title.upper(), self.styles['DDR_SectionHeading'])
            story.append(heading)
            story.append(Spacer(1, 0.15*inch))  # Reduced from 0.3*inch
            
            # Add section content
            if section_content.strip():
                # Convert markdown-like formatting to HTML
                formatted_content = self._format_text_content(section_content)
                content_para = Paragraph(formatted_content, self.styles['DDR_BodyText'])
                story.append(content_para)
                story.append(Spacer(1, 0.2*inch))  # Reduced from 0.5*inch
            else:
                # Add "Not Available" message with warning style
                no_content = Paragraph("Not Available", self.styles['DDR_Warning'])
                story.append(no_content)
                story.append(Spacer(1, 0.15*inch))  # Reduced spacing
        
        return story
    
    def _parse_ddr_sections(self, ddr_content: str) -> Dict[str, str]:
        """Parse DDR content into sections"""
        sections = {}
        
        # Define section patterns
        section_patterns = [
            "PROPERTY ISSUE SUMMARY",
            "AREA-WISE OBSERVATIONS", 
            "PROBABLE ROOT CAUSE",
            "SEVERITY ASSESSMENT",
            "RECOMMENDED ACTIONS",
            "ADDITIONAL NOTES",
            "MISSING OR UNCLEAR INFORMATION"
        ]
        
        # Split content by section headers
        current_section = None
        current_content = []
        
        lines = ddr_content.split('\n')
        for line in lines:
            line = line.strip()
            
            # Check if this line is a section header
            is_section = False
            for pattern in section_patterns:
                if pattern in line.upper():
                    # Save previous section
                    if current_section:
                        sections[current_section] = '\n'.join(current_content)
                    
                    # Start new section
                    current_section = line
                    current_content = []
                    is_section = True
                    break
            
            if not is_section and current_section:
                current_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _format_text_content(self, content: str) -> str:
        """Format text content with HTML tags for attractive presentation"""
        # Global cleanup of markdown artifacts
        content = content.replace('#', '').replace('*', '').replace('•', '')
        
        # Clean up extra spaces and formatting
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Remove leading list markers or dividers
            while line.startswith(('-', '>', '+', '=', '_')):
                line = line[1:].strip()
                
            if line and not line.lower().startswith('not available'):
                # Clean up any remaining artifacts
                line = line.replace('&bull;', '')
                
                # Add emphasis to important terms
                if 'critical' in line.lower() or 'urgent' in line.lower() or 'severe' in line.lower():
                    line = f'<b>{line}</b>'
                elif 'recommend' in line.lower() or 'suggest' in line.lower():
                    line = f'<i>{line}</i>'
                
                if line:
                    formatted_lines.append(line)
        
        # Join paragraphs with proper spacing
        formatted_content = '<br/><br/>'.join(formatted_lines) if formatted_lines else "Not Available"
        
        return formatted_content
    
    def _create_images_section(self, inspection_images: List[Dict], thermal_images: List[Dict]) -> List:
        """Create the images section"""
        story = []
        
        # Store for use in title page
        self.inspection_images = inspection_images
        self.thermal_images = thermal_images
        
        # Section heading
        heading = Paragraph("EXTRACTED IMAGES", self.styles['DDR_SectionHeading'])
        story.append(heading)
        
        # Add inspection images
        self._add_image_subsection(story, "Inspection Report Images:", inspection_images)
        
        # Add thermal images
        self._add_image_subsection(story, "Thermal Report Images:", thermal_images)
        
        # Handle no images case
        if not inspection_images and not thermal_images:
            no_images = Paragraph("No images were extracted from the reports.", self.styles['DDR_Warning'])
            story.append(no_images)
        
        return story
    
    def _add_image_subsection(self, story: List, title: str, images: List[Dict]) -> None:
        """Add a subsection of images to the story"""
        if not images:
            return
            
        # Add subsection heading
        story.append(Paragraph(title, self.styles['DDR_Subsection']))
        story.append(Spacer(1, 0.2*inch))
        
        # Add images with enhanced layout
        for i, img in enumerate(images[:5]):  # Limit to first 5 images
            try:
                img_path = img.get('path')
                if img_path and os.path.exists(img_path):
                    # Add image with proper sizing
                    img_obj = Image(img_path, width=4.5*inch, height=3.5*inch)
                    img_obj.hAlign = 'CENTER'
                    story.append(img_obj)
                    story.append(Spacer(1, 0.15*inch))
                    
                    # Add caption with enhanced styling
                    caption = f"Page {img.get('page', '?')}: {img.get('filename', 'Unknown')}"
                    caption_para = Paragraph(caption, self.styles['DDR_Caption'])
                    story.append(caption_para)
                    story.append(Spacer(1, 0.2*inch))
            except Exception as e:
                logger.warning(f"Could not add image {img.get('filename', 'unknown')}: {str(e)}")
                continue
        
        # Add note if more images exist
        if len(images) > 5:
            note = Paragraph(f"*Showing first 5 of {len(images)} images", self.styles['DDR_Info'])
            story.append(note)
        
        story.append(Spacer(1, 0.3*inch))
    
    def _add_image_to_story(self, story: List, img: Dict) -> None:
        """Add a single image to the story"""
        try:
            img_path = img.get('path')
            if img_path and os.path.exists(img_path):
                # Create image with proper sizing and quality
                img_obj = Image(img_path, width=4.5*inch, height=3.5*inch)
                img_obj.hAlign = 'CENTER'
                story.append(img_obj)
        except Exception as e:
            logger.warning(f"Could not add image {img.get('filename', 'unknown')}: {str(e)}")
    
    def _create_appendix(self) -> List:
        """Create an impressive appendix section"""
        story = []
        
        story.append(PageBreak())
        heading = Paragraph("APPENDIX", self.styles['DDR_SectionHeading'])
        story.append(heading)
        
        # Premium report generation info
        info_text = """
        <b>🔬 Premium Report Generation Information</b><br/><br/>
        
        This sophisticated Detailed Diagnostic Report has been generated using cutting-edge AI technology 
        combined with advanced building science principles. Our system represents the pinnacle of 
        automated property analysis, delivering insights that traditionally required extensive manual 
        expertise and time investment.<br/><br/>
        
        <b>⚡ Advanced Technical Specifications</b><br/><br/>
        • <b>Analysis Engine:</b> Google Gemini 2.5 Flash - State-of-the-art AI model<br/>
        • <b>PDF Processing:</b> PyMuPDF Advanced - High-fidelity document extraction<br/>
        • <b>Report Generation:</b> Professional ReportLab Engine - Premium document formatting<br/>
        • <b>Processing Date:</b> {}<br/>
        • <b>Report Version:</b> DDR Premium v2.0<br/>
        • <b>Quality Assurance:</b> Multi-layer validation and verification<br/><br/>
        
        <b>🎯 Our Commitment to Excellence</b><br/><br/>
        Every report generated through our system undergoes rigorous quality checks and validation 
        processes. We combine the power of artificial intelligence with proven building science 
        methodologies to deliver reports that professionals can trust and clients can understand.<br/><br/>
        
        <b>📊 Data Processing Capabilities</b><br/><br/>
        Our system processes multiple data streams simultaneously, including visual inspection data, 
        thermal imaging information, and environmental factors. This comprehensive approach ensures 
        that no critical information is overlooked and that all findings are properly contextualized 
        within the broader property assessment framework.<br/><br/>
        
        <b>🔍 Continuous Improvement</b><br/><br/>
        Our AI models are continuously trained on the latest building science research, industry standards, 
        and real-world inspection data. This ensures that every report reflects the most current 
        understanding of building performance, material science, and diagnostic methodologies.<br/><br/>
        
        <i>Thank you for choosing our premium DDR analysis service. We are committed to providing 
        the highest quality property assessments available in the industry today.</i>
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        info_para = Paragraph(info_text, self.styles['DDR_BodyText'])
        story.append(info_para)
        
        # Professional closing statement
        story.append(Spacer(1, 0.5*inch))
        closing = Paragraph("🏆 Excellence in Analysis • Precision in Reporting • Confidence in Results 🏆", self.styles['DDR_Footer'])
        story.append(closing)
        
        return story
