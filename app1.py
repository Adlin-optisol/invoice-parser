import streamlit as st
import os
import tempfile
import logging
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from dotenv import load_dotenv
from elsai_core.model import AzureOpenAIConnector
from elsai_core.config.loggerConfig import setup_logger
from invoice_prompts import get_prompt_by_type  # Import the prompt function

# Set up logging

# Initialize logger
logger = setup_logger()

# Load environment variables
try:
    load_dotenv()
    logger.info("Environment variables loaded successfully")
except Exception as e:
    logger.error(f"Failed to load environment variables: {str(e)}")

# Set page configuration
st.set_page_config(
    page_title="Invoice Parser",
    page_icon="📄",
    layout="wide"
)

# App title and description
st.title("Invoice Parser")
st.markdown("Upload PDF invoices or timesheets to extract structured data")

def extract_content_from_pdf(pdf_path):
    """
    Extract tables and text from a PDF file using Azure Document Intelligence.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        tuple: (extracted_text, extracted_tables)
    """
    logger.info(f"Starting extraction from PDF: {os.path.basename(pdf_path)}")
    
    try:
        # Get Azure credentials from environment variables
        endpoint = os.getenv("VISION_ENDPOINT")
        key = os.getenv("VISION_KEY")
        
        if not endpoint or not key:
            logger.error("Azure Document Intelligence credentials not found in environment variables")
            raise ValueError("Azure Document Intelligence credentials not found in environment variables")
        
        # Initialize the Document Intelligence client
        document_intelligence_client = DocumentIntelligenceClient(
            endpoint=endpoint, 
            credential=AzureKeyCredential(key)
        )
        logger.debug("Document Intelligence client initialized")
        
        # Process the PDF file
        with open(pdf_path, "rb") as f:
            logger.info("Beginning document analysis")
            poller = document_intelligence_client.begin_analyze_document("prebuilt-layout", body=f)
        
        # Get the result
        logger.info("Waiting for document analysis to complete")
        result = poller.result()
        logger.info("Document analysis completed successfully")
        
        # Extract text content
        logger.debug("Extracting text content")
        extracted_text = extract_text(result)
        
        # Extract tables
        logger.debug("Extracting tables")
        extracted_tables = extract_tables(result)
        
        logger.info(f"Extraction complete. Found {len(extracted_text)} pages of text and {len(extracted_tables)} tables")
        return extracted_text, extracted_tables
    
    except Exception as e:
        logger.error(f"Error extracting content from PDF: {str(e)}", exc_info=True)
        raise

def extract_text(result):
    """
    Extract text content from the analysis result.
    
    Args:
        result: The result from Document Intelligence analysis
        
    Returns:
        dict: Dictionary containing text content by page
    """
    logger.debug("Starting text extraction from analysis result")
    text_content = {}
    
    # Extract text from paragraphs (most reliable for formatted text)
    if result.paragraphs:
        logger.debug(f"Found {len(result.paragraphs)} paragraphs to extract")
        # Sort paragraphs by their position in the document
        sorted_paragraphs = sorted(
            result.paragraphs, 
            key=lambda p: (p.spans[0].offset if p.spans else 0)
        )
        
        for paragraph in sorted_paragraphs:
            page_numbers = [region.page_number for region in paragraph.bounding_regions] if paragraph.bounding_regions else []
            
            for page_num in page_numbers:
                if page_num not in text_content:
                    text_content[page_num] = []
                
                text_content[page_num].append({
                    "type": "paragraph",
                    "content": paragraph.content,
                    "role": paragraph.role if hasattr(paragraph, "role") else None
                })
    
    # If no paragraphs, extract text from pages
    if not text_content and result.pages:
        logger.debug(f"No paragraphs found, extracting from {len(result.pages)} pages")
        for page in result.pages:
            page_num = page.page_number
            text_content[page_num] = []
            
            if page.lines:
                for line in page.lines:
                    text_content[page_num].append({
                        "type": "line",
                        "content": line.content
                    })
    
    logger.debug(f"Text extraction complete. Extracted text from {len(text_content)} pages")
    return text_content

def extract_tables(result):
    """
    Extract tables from the analysis result.
    
    Args:
        result: The result from Document Intelligence analysis
        
    Returns:
        list: List of dictionaries containing table data
    """
    logger.debug("Starting table extraction from analysis result")
    extracted_tables = []
    
    if result.tables:
        logger.debug(f"Found {len(result.tables)} tables to extract")
        for table_idx, table in enumerate(result.tables):
            logger.debug(f"Processing table {table_idx+1} with {table.row_count} rows and {table.column_count} columns")
            # Create a table representation
            table_data = {
                "table_id": table_idx,
                "row_count": table.row_count,
                "column_count": table.column_count,
                "page_numbers": [],
                "cells": []
            }
            
            # Add page numbers where this table appears
            if table.bounding_regions:
                for region in table.bounding_regions:
                    if region.page_number not in table_data["page_numbers"]:
                        table_data["page_numbers"].append(region.page_number)
            
            # Extract cell data
            for cell in table.cells:
                cell_data = {
                    "row_index": cell.row_index,
                    "column_index": cell.column_index,
                    "content": cell.content,
                    "is_header": cell.kind == "columnHeader" if hasattr(cell, "kind") else False,
                    "spans": cell.column_span if hasattr(cell, "column_span") else 1
                }
                table_data["cells"].append(cell_data)
            
            extracted_tables.append(table_data)
            logger.debug(f"Extracted table {table_idx+1} with {len(table_data['cells'])} cells")
    
    logger.debug(f"Table extraction complete. Extracted {len(extracted_tables)} tables")
    return extracted_tables

def format_table_as_markdown(table_data):
    """
    Format extracted table data as markdown table.
    
    Args:
        table_data (dict): Table data dictionary
        
    Returns:
        str: Markdown formatted table
    """
    logger.debug(f"Formatting table {table_data.get('table_id', 'unknown')} as markdown")
    if not table_data or not table_data["cells"]:
        logger.warning("Empty table data received for markdown formatting")
        return "Empty table"
    
    # Get dimensions
    rows = table_data["row_count"]
    cols = table_data["column_count"]
    
    # Create empty grid
    grid = [["" for _ in range(cols)] for _ in range(rows)]
    
    # Fill in the grid with cell content
    for cell in table_data["cells"]:
        row = cell["row_index"]
        col = cell["column_index"]
        grid[row][col] = cell["content"]
    
    # Convert to markdown
    markdown = []
    
    # Header row
    markdown.append("| " + " | ".join(grid[0]) + " |")
    
    # Header separator
    markdown.append("| " + " | ".join(["---" for _ in range(cols)]) + " |")
    
    # Data rows
    for row in grid[1:]:
        markdown.append("| " + " | ".join(row) + " |")
    
    logger.debug("Table markdown formatting complete")
    return "\n".join(markdown)

def convert_to_markdown(text_content, tables):
    """
    Convert extracted text and tables to a single markdown string.
    
    Args:
        text_content (dict): Extracted text content by page
        tables (list): Extracted tables
        
    Returns:
        str: Combined markdown formatted string
    """
    logger.debug("Converting extracted content to markdown")
    markdown_parts = []
    
    # Add document title
    markdown_parts.append("# Extracted PDF Content\n")
    
    # Add text content
    markdown_parts.append("## Text Content\n")
    for page_num in sorted(text_content.keys()):
        markdown_parts.append(f"### Page {page_num}\n")
        for item in text_content[page_num]:
            markdown_parts.append(item["content"])
            markdown_parts.append("\n")
        markdown_parts.append("\n")
    
    # Add tables
    if tables:
        markdown_parts.append("## Tables\n")
        for i, table in enumerate(tables):
            markdown_parts.append(f"### Table {i+1}\n")
            markdown_parts.append(f"*Pages: {', '.join(map(str, table['page_numbers']))}*\n\n")
            markdown_parts.append(format_table_as_markdown(table))
            markdown_parts.append("\n\n")
    
    logger.debug("Markdown conversion complete")
    return "".join(markdown_parts)

def process_pdf(uploaded_file, document_type):
    """
    Process an uploaded PDF file.
    
    Args:
        uploaded_file: The uploaded file object from Streamlit
        document_type: The type of document ('invoice', 'timesheet', or 'both')
        
    Returns:
        str: Markdown formatted results
    """
    file_name = uploaded_file.name
    logger.info(f"Processing PDF file: {file_name} as {document_type}")
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name
        logger.debug(f"Created temporary file: {tmp_path}")
    
    try:
        # Extract content from PDF
        logger.info("Extracting content from PDF")
        text_content, tables = extract_content_from_pdf(tmp_path)
        
        # Convert to markdown
        logger.info("Converting extracted content to markdown")
        markdown_content = convert_to_markdown(text_content, tables)
        logger.debug("Markdown conversion completed")
        
        # Process with LLM
        logger.info("Initializing LLM connector")
        connector = AzureOpenAIConnector()
        llm = connector.connect_azure_open_ai(deploymentname="gpt-4o-mini")
        logger.info("LLM connector initialized")
        
        # Get appropriate prompt based on document type
        logger.info(f"Getting prompt for document type: {document_type}")
        prompt = get_prompt_by_type(document_type, markdown_content)
        
        logger.info("Sending request to LLM")
        response = llm.invoke(prompt)
        result = response.content
        logger.info(f"Received response from LLM ({len(result)} characters)")
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing PDF {file_name}: {str(e)}", exc_info=True)
        return f"Error processing PDF: {str(e)}"
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_path):
            logger.debug(f"Cleaning up temporary file: {tmp_path}")
            os.unlink(tmp_path)
            logger.debug("Temporary file removed")

# Create the Streamlit UI
def main():
    logger.info("Starting Invoice Parser application")
    
    # File uploader
    uploaded_files = st.file_uploader("Upload PDF invoices or timesheets", 
                                     type=['pdf'], 
                                     accept_multiple_files=True)
    
    # Document type selection dropdown
    document_type = st.selectbox(
        "Select document type",
        options=["Invoice", "Timesheet", "Digital Invoice and Timesheet", "Multiple Timesheets"],
        help="Select the type of document you are uploading"
    )
    logger.info(f"Document type selected: {document_type}")
    
    if uploaded_files:
        logger.info(f"{len(uploaded_files)} files uploaded")
        
        if st.button("Process Files"):
            logger.info("Process Files button clicked")
            
            with st.spinner("Processing files..."):
                # Process each file
                for uploaded_file in uploaded_files:
                    logger.info(f"Processing file: {uploaded_file.name}")
                    st.subheader(f"Processing: {uploaded_file.name}")
                    
                    # Process the file with the selected document type
                    result = process_pdf(uploaded_file, document_type)
                    
                    # Create a container for the rendered markdown
                    table_container = st.container()
                    with table_container:
                        # Render the markdown as a table
                        st.markdown(result, unsafe_allow_html=True)
                    
                    # Add a divider between files
                    st.markdown("---")
                    logger.info(f"Completed processing file: {uploaded_file.name}")
                
                logger.info("All files processed successfully")
                st.success("All files processed successfully!")

# Run the app
if __name__ == "__main__":
    try:
        logger.info("Application starting")
        main()
        logger.info("Application ended normally")
    except Exception as e:
        logger.critical(f"Unhandled exception in main application: {str(e)}", exc_info=True)
        st.error(f"An unexpected error occurred: {str(e)}")