from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Link
from reportlab.lib.colors import blue
import os
from datetime import datetime
import re
import uuid

def parse_markdown_link(text):
    """
    Parse Markdown-style links [text](url)
    
    Returns:
        tuple: (display_text, url) or (original_text, None)
    """
    # Regex to match Markdown links [text](url)
    match = re.match(r'\[([^\]]+)\]\(([^\)]+)\)', text)
    if match:
        return match.group(1), match.group(2)
    return text, None

def create_colored_paragraph(text, styles, is_link=False):
    """
    Create a paragraph with optional link coloring
    
    Args:
        text (str): Text to display
        styles (dict): ReportLab styles
        is_link (bool): Whether to style as a link
        
    Returns:
        Paragraph: Formatted paragraph
    """
    # Create a copy of the normal style to modify
    link_style = ParagraphStyle(
        'LinkStyle',
        parent=styles['Normal'],
        textColor=blue if is_link else colors.black,
        underline=1 if is_link else 0
    )
    
    return Paragraph(text, link_style)

def generate_travel_document(all_tables, document_filename):
    """
    Generate a beautifully formatted PDF travel document from ASCII tables.
    
    Args:
        all_tables (str): Concatenated string of formatted ASCII tables
        document_filename (str): Base filename for the PDF (without extension)
        
    Returns:
        str: Path to the generated PDF file
    """
    # Ensure the filename has .pdf extension
    if not document_filename.lower().endswith('.pdf'):
        document_filename += '.pdf'
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        document_filename,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Prepare styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        spaceAfter=8
    )
    
    # Initialize story (content)
    story = []
    
    # Add title
    title = "Travel Itinerary"
    story.append(Paragraph(title, title_style))
    
    # Add generation date
    date_str = datetime.now().strftime("%B %d, %Y")
    story.append(Paragraph(f"Generated on {date_str}", normal_style))
    story.append(Spacer(1, 20))
    
    # Function to process table string into reportlab table
    def create_reportlab_table(table_str):
        if not table_str:
            return None
            
        # Split the table string into lines
        lines = table_str.split('\n')
        
        # Remove ASCII borders and extract data
        data = []
        for line in lines:
            if '|' in line:  # Only process lines with actual data
                # Split by |, strip spaces, and remove empty strings
                row = [cell.strip() for cell in line.split('|')]
                row = [cell for cell in row if cell]
                if row:  # Only add non-empty rows
                    # Parse links in each cell
                    parsed_row = []
                    for cell in row:
                        display_text, url = parse_markdown_link(cell)
                        parsed_row.append((display_text, url))
                    data.append(parsed_row)
        
        if not data:
            return None
            
        # Prepare table data for ReportLab
        processed_data = []
        for row in data:
            processed_row = []
            for text, url in row:
                if url:
                    # Create a blue, underlined paragraph for links
                    processed_row.append(create_colored_paragraph(text, styles, is_link=True))
                else:
                    # Regular text
                    processed_row.append(create_colored_paragraph(text, styles))
            processed_data.append(processed_row)
        
        # Create Table object
        table = Table(processed_data, repeatRows=1)
        
        # Add style
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f3f7')),  # Header background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),   # Header text color
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
        ]))
        
        return table
    
    # Add each table to the document
    tables = all_tables.split('\n\n')
    for table_str in tables:
        if table_str.strip():
            # Create and add table
            table = create_reportlab_table(table_str)
            if table:
                story.append(table)
                story.append(Spacer(1, 20))
    
    # Add footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        textColor=colors.gray,
        fontSize=8,
        alignment=1
    )
    footer_text = "Generated by PocketTraveller Travel Planning System"
    story.append(Spacer(1, 30))
    story.append(Paragraph(footer_text, footer_style))
    
    # Build the PDF
    doc.build(story)
    
    return document_filename





