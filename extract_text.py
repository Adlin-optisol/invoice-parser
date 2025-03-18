import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from dotenv import load_dotenv
from elsai_core.model import AzureOpenAIConnector
load_dotenv()

def extract_content_from_pdf(pdf_path):
    """
    Extract tables and text from a PDF file using Azure Document Intelligence.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        tuple: (extracted_text, extracted_tables)
    """
    # Get Azure credentials from environment variables
    endpoint = os.environ.get("VISION_ENDPOINT")
    key = os.environ.get("VISION_KEY")
    
    if not endpoint or not key:
        raise ValueError("Azure Document Intelligence credentials not found in environment variables")
    
    # Initialize the Document Intelligence client
    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=endpoint, 
        credential=AzureKeyCredential(key)
    )
    
    # Process the PDF file
    with open(pdf_path, "rb") as f:
        poller = document_intelligence_client.begin_analyze_document("prebuilt-layout", body=f)
    
    # Get the result
    result = poller.result()
    
    # Extract text content
    extracted_text = extract_text(result)
    
    # Extract tables
    extracted_tables = extract_tables(result)
    
    return extracted_text, extracted_tables

def extract_text(result):
    """
    Extract text content from the analysis result.
    
    Args:
        result: The result from Document Intelligence analysis
        
    Returns:
        dict: Dictionary containing text content by page
    """
    text_content = {}
    
    # Extract text from paragraphs (most reliable for formatted text)
    if result.paragraphs:
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
        for page in result.pages:
            page_num = page.page_number
            text_content[page_num] = []
            
            if page.lines:
                for line in page.lines:
                    text_content[page_num].append({
                        "type": "line",
                        "content": line.content
                    })
    
    return text_content

def extract_tables(result):
    """
    Extract tables from the analysis result.
    
    Args:
        result: The result from Document Intelligence analysis
        
    Returns:
        list: List of dictionaries containing table data
    """
    extracted_tables = []
    
    if result.tables:
        for table_idx, table in enumerate(result.tables):
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
    
    return extracted_tables

def format_table_as_markdown(table_data):
    """
    Format extracted table data as markdown table.
    
    Args:
        table_data (dict): Table data dictionary
        
    Returns:
        str: Markdown formatted table
    """
    if not table_data or not table_data["cells"]:
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
    
    return "".join(markdown_parts)

def main():
    # Example usage
    pdf_path = "DGRADY 22112024.pdf"  # Using your PDF path
    
    try:
        print(f"Extracting content from {pdf_path}...")
        text_content, tables = extract_content_from_pdf(pdf_path)
        
        # Convert to markdown
        markdown_content = convert_to_markdown(text_content, tables)
        # Print summary
        print(f"Extracted content from {len(text_content)} pages and {len(tables)} tables.")
        connector = AzureOpenAIConnector()

# Connect to Azure OpenAI deployment
        llm = connector.connect_azure_open_ai(deploymentname="gpt-4o-mini")
        prompt_4 = f"""### Unified Prompt for Invoice and Timesheet Data Extraction
        #### **Identify Document Type**
        - Analyze the content to determine if the document is an **Invoice**, a **Timesheet**, or both.
        - Extract relevant fields based on the identified document type.
        - Choose the most suitable timesheet data extraction set with the most complete or accurate information.
        - The content is as follows:
        {markdown_content}
        ---

        ### **Invoice Data Extraction**

        #### **Extract Invoice Header Information**
        - Invoice Number
        - Invoice Date
        - Invoice Terms
        - Due Date
        - Page Number

        #### **Extract Company Details**
        - Company Name
        - Company Address
        - Company Phone Number	
        - Company Mobile Number
        - Company Email

        #### **Extract Client Details**
        - Client Name
        - Client Address

        #### **Extract Invoice Line Items** (this may have mutltiple records . be sure to extract all)
        - Job Order No
        - Purchase Order No
        - Payee Name
        - Weekending Date
        - Description
        - Item
        - Quantity
        - Rate
        - Invoice Amount (ex. Tax)

        #### **Extract Bank Details**
        - Bank Name
        - BSB (Bank-State-Branch)
        - Account Number

        #### **Extract Invoice Totals**
        - Sub Total
        - GST
        - Total Amount

        ---

        ### **Timesheet Data Extraction**

        - Choose **Set 1** or **Set 2** for timesheet data extraction based on the amount of information or accuracy.
        - Donot mention if its**Set 1** or **Set 2** in the final json 

        #### **Set 1: Extract Timesheet Header Information**
        - Payee No
        - Payee Name
        - Job Order
        - Job Description
        - Client Number 
        - Client Name
        - Weekending Date

        #### **Extract Timesheet Attendance Details**
        - Date
        - Start Time
        - End Time
        - Attendance/Absence Type
        - Total Hours

        #### **Extract Additional Items**
        - Date
        - Item Description
        - Quantity

        #### **Extract Reimbursement Comments**
        - Comment Date
        - Created Date & Time
        - Created By
        - Comment
        - Display to Candidate (Yes/No)
        - Display to Client Contact (Yes/No)

        #### **Extract Timesheet Totals**
        - Total Scheduled Hours
        - Total Attendance Hours
        - Total Absence Hours

        ---

        #### **Set 2: Employee Details**
        - Employee Name
        - Employee Code (is not Crane logistics or EWP )
        - Type( Crane logistics or EWP )

        #### **Allowances (KM's Section)**
        - KM's Allowance 1 (with checkbox and description)
        - KM's Allowance 2 (with checkbox and description)

        #### **Location Details**
        - Starting Location
        - End Location

        #### **Compliance Checks**
        - 10-Hour Break Since Last Shift (YES/NO)
        - Lunch Break Taken (YES/NO)
        - Next Shift 10-Hour Break Compliance (YES/NO)
        - Incident/Injury Occurred (YES/NO, requires incident report if YES)

        #### **Shift Details Table**
        - Start Time
        - Finish Time
        - Meal  Break(consider this field as a checkbox)
        - Total Hours
        - Crane Operator(consider this field as a checkbox)
        - Rigger/Dogman(consider this field as a checkbox)
        - Truck Driver(consider this field as a checkbox)
        - Travel Tower Operator(consider this field as a checkbox)
        - Mechanic(consider this field as a checkbox)
        - Other(consider this field as a checkbox)
        - Asset Number
        - Hire Docket/Work Order Number
        - Customer Name
        - Description (e.g., Come size, TT size, Travel, Induction, Medical, Work in Yard, etc.) (could have multiple values)
        - Job Code
        - Job Complete (Y/N)

        #### **Approval Section (for No Lunch Break)**
        - Authorised By (name)

        #### **Document Metadata**
        - Document Number (e.g., NAT-FM-PR-0109)
        - Issue Date (e.g., 30/09/14)

        ---

        ### **General Instructions**

        #### **Handle Multi-Page Documents**
        - Ensure data is extracted from all pages, including headers, tables, and footers.

        #### **Validate Extracted Data**
        - Perform cross-checks for consistency and completeness.
        - Ignore missing or inconsistent fields.

        #### **Handle Checkboxes and Free-Text Fields**
        - For checkbox fields (e.g., YES/NO), extract the selected option. 
        - For free-text fields (e.g., allowances, descriptions), extract the text as-is. If empty, ignore it.

        #### **Output Structured Data**
        - Present the extracted information as a clear, well-structured table with appropriate field labels in markdown format .
        - Choose the correct set (Set 1 or Set 2) for timesheet extraction. Only one set should be included in the final table.
        - Donot include missing fields ,empty key-value pairs . just give table no need to give summary .
        """
        response = llm.invoke(prompt_4)
        print(response.content) 
    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Error extracting content: {str(e)}"

if __name__ == "__main__":
    main()