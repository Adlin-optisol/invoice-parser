# invoice_prompts.py
"""
This module contains the prompts for different types of document processing.
"""

def get_invoice_prompt(markdown_content):
    """
    Returns the prompt for invoice data extraction.
    
    Args:
        markdown_content (str): The markdown content extracted from the PDF
        
    Returns:
        str: The prompt for invoice processing
    """
    return f"""### Invoice Data Extraction Prompt
    
    ####  Invoice Header Information**
    - Invoice Number
    - Invoice Date
    - Invoice Terms
    - Due Date
    - Page Number

    ####  Company Details**
    - Company Name
    - Company Address
    - Company Phone Number	
    - Company Mobile Number
    - Company Email

    ####  Client Details**
    - Client Name
    - Client Address

    ####  Invoice Line Items** (this may have multiple records. The following are the headers of the table and the multiple records should be as rows in the table)
    - Job Order No
    - Purchase Order No
    - Payee Name
    - Weekending Date
    - Description
    - Item
    - Quantity
    - Rate
    - Invoice Amount (ex. Tax)

    ####  Bank Details**
    - Bank Name
    - BSB (Bank-State-Branch)
    - Account Number

    ####  Invoice Totals**
    - Sub Total
    - GST
    - Total Amount

    #### **General Instructions**
    - Ensure data is extracted from all pages, including headers, tables, and footers.
    - Perform cross-checks for consistency and completeness.
    - Present the extracted information as a clear, well-structured table with appropriate field labels in markdown format.
    - Donot include missing fields, empty key-value pairs. Just give table, no need to give summary.
    - IMPORTANT: Use valid markdown table format. Ensure the table has header rows, separator rows, and proper cell alignment.
    
    The content is as follows:
    {markdown_content}
    """

def get_timesheet_prompt(markdown_content):
    """
    Returns the prompt for timesheet data extraction.
    
    Args:
        markdown_content (str): The markdown content extracted from the PDF
        
    Returns:
        str: The prompt for timesheet processing
    """
    return  f"""
        **GENERAL INSTRUCTION**

        - The timesheet follows either **Set 1** or **Set 2** format. Choose the most suitable set based on the **context**.
        - **ONLY include the defined parameters from Set 1 or Set 2** in the final output.  
        - **Map values from the content (tables and text) to the defined parameters only.**
        - **Ignore unmapped values** — do **not** include them.
        - **Extract relevant fields based on the context**.
        - Choose the **most complete and accurate** timesheet data extraction set.
        - The context provided could be from a **single timesheet** or **multiple timesheets**.

        #### **IMPORTANT for MULTIPLE TIMESHEETS:**
        - If the content contains **a series of timesheets**, ensure that **each timesheet is distinctly identified**.
        - However, distinctly identify the rows from different timesheets in the output, include the **Employee Name** and **Date** (from the same page) **in each corresponding record/row** to maintain clarity.
        - This distinction can be made by referring to the **page number or section header in the context**.
        - Ensure that **all records grouped in a table share the same Employee Name and Date values from their respective page/context**.

        ### **IMPORTANT FOR TIME SHEETS**
        - When a single column in a row is filled add it to the previous row
        -Likewise when more than one column is filled in a single row  ADD IT AS A NEW ROW TO THE TABLE

        ---

        ### **Timesheet Data Extraction** *(include as title)*

        - Choose **Set 1** or **Set 2** based on completeness or accuracy of data.
        - **Do not mention "Set 1" or "Set 2"** in the final JSON output or markdown table.

        #### **Set 1: Extract Timesheet Header Information**
        - Payee No  
        - Payee Name  
        - Job Order  
        - Job Description  
        - Client Number  
        - Client Name  
        - Weekending Date  

        ####  Timesheet Attendance Details**
        - Date  
        - Start Time  
        - End Time  
        - Attendance/Absence Type  
        - Total Hours  

        ####  Additional Items**
        - Date  
        - Item Description  
        - Quantity  

        ####  Reimbursement Comments**
        - Comment Date  
        - Created Date & Time  
        - Created By  
        - Comment  
        - Display to Candidate (Yes/No)  
        - Display to Client Contact (Yes/No)  

        ####  Timesheet Totals**
        - Total Scheduled Hours  
        - Total Attendance Hours  
        - Total Absence Hours  

        ---

        #### **Set 2: Employee Details**
        *(If the timesheet follows this format, render each section (####) as a separate markdown table)*

        - Employee Name  
        - Employee Code *(Only if not "Crane logistics" or "EWP")*  
        - Type *(Crane logistics or EWP)*  
        - Depot  
        - Date  
        - Day *(Predict the day from the date parameter value and map it to the day parameter use Zeller’s Congruence if needed to find out the day)*

        #### **Allowances (KM's Section)**
        - Employee Name 
        - Date
        - KM's Allowance 1 *(with checkbox and description)*  
        - KM's Allowance 2 *(with checkbox and description)*  

        #### **Location Details**
        - Employee Name 
        - Date
        - Starting Location  
        - End Location  

        #### **Compliance Checks**
        - Employee Name 
        - Date
        - 10-Hour Break Since Last Shift (YES/NO)   
        - Lunch Break Taken (YES/NO)  
        - Next Shift 10-Hour Break Compliance (YES/NO) 
        - Incident/Injury Occurred (YES/NO, with incident report if YES) 

        #### **Shift Details Table**
        *("Description" can have multiple records; extract each record as a separate row. The following are the headers for this table)*
        *(if empty , fill N/A)*
        *(the 11th column should only be mapped to ASSET NO, And the value in the column before the customer name should be mapped to the HIREDOCKET COLUMN, Do not make any changes to other columns)
        - Employee Name 
        - Date
        - Start Time  
            - Values must be in HH:MM 24 hours format 
        - Finish Time  
            - Values must be in HH:MM 24 hours format 
        - Total Hours   
            - when start time and finish time is empty , fill total hours as N/A
        - Crane Operator *(checkbox)*  
            - map selected to YES and unselected to NO 
        - Rigger/Dogman *(checkbox)*  
            - map selected to YES and unselected to NO
        - Truck Driver *(checkbox)*  
            - map selected to YES and unselected to NO
        - Travel Tower Operator *(checkbox)* 
            - map selected to YES and unselected to NO
        - Mechanic *(checkbox)*  
            - map selected to YES and unselected to NO
        - Other *(checkbox)*  
            - map selected to YES and unselected to NO
        - Asset Number  
            - *(IMPORTANT: YOU MUST MAP THE VALUE FROM THE 11TH COLUMN IN THE TABLE TO THIS PARAMETER. DO NOT USE THIS VALUE FOR ASSET NUMBER)*
            - *(Enter ONLY genuine asset numbers in this field)*
            - *(Do NOT copy or duplicate the Hire Docket/Work Order Number into this field)*
            - *(If no distinct asset number is provided, leave this field blank or mark as "N/A")*
            -*(Donot map start time or finish time into this)*
        - Hire Docket/Work Order Number  - (Values must be number only OR N/A) 
            *(IMPORTANT: YOU MUST MAP THE VALUE FROM THE 12TH COLUMN IN THE TABLE TO THIS PARAMETER. DO NOT USE THIS VALUE FOR ASSET NUMBER)*(The value in the column before Customer Name should be considered for Hire docket only applicable for this column dont make any changes to other columns, THIS IS ALWAYS APPLICABLE FOR EVERY ROW)
            **HIRE DOCKET/ WORK ORDER NUMBER COLUMN CAN NEVER HAVE SINGLE DIGIT VALUES, FILL AS N/A IF IT DOES HAVE SINGLE DIGIT VALUES**
        - Customer Name  
            - Values must be text only
        - Description  
            - Values must be text only , is a description of the job done for the day
        - Job Code  
            - ALWAYS FILL AS N/A
        - Job Complete (Y/N) 
            - map y to YES and n to NO 


        #### **Document Metadata**
        - Document Number (e.g., NAT-FM-PR-0109)  
        - Issue Date (e.g., 30/09/14)  

        ---

        ### **General Instructions**

        #### **Handle Multi-Page Documents**
        - Extract data from **all pages**, including headers, tables, and footers.

        #### **Validate Extracted Data**
        - Perform **cross-checks** for consistency and completeness.
        - **Ignore** missing or inconsistent fields.

        #### **Handle Checkboxes and Free-Text Fields**
        - Extract the selected **checkbox value (YES/NO)**.  
        - For **free-text fields** (e.g., descriptions, comments), extract the text as-is. If empty, ignore it.

        #### **Output Structured Data**
        - Output the extracted data as **well-structured markdown tables with appropriate field labels**.
        - **Only one set (Set 1 or Set 2)** should be selected and extracted per timesheet context.
        - Within the chosen set, **include only available fields**—**do not** leave empty cells or include missing fields.
        - **Do not include summary or extra explanations.**
        - **map selected to YES and unselected to NO** , there should be no cell with the values selected or unselected, if there is , they should be replaced with YES or NO respectively.
        - **Ensure markdown table formatting is valid**: headers, separators, and aligned cells must be used correctly.
        - **IMPORTANT** Remember to map the 12th column specifically to the Hire Docket/Work Order Number field, not to the Asset Number field.
        - **EXTREMELY IMPORTANT If only one column in a row is filled, merge its data with the previous row. If multiple columns are filled in a single row, add it as a new entry in the table.
        - ** INCLUDE THE COMPLIANCE CHECK TABLE ALSO FOR SET 2 IN TIMESHEET EXTRACTION
        -**DONOT MAP THE START TIME, FINISH TIME INTO THE ASSET NUMBER.
        -**IF START TIME, FINISH TIME IS EMPTY OR N/A THE TOTAL HOURS SHOULD BE N/AFOR TIMESHEET EXTRACTION SET 2 ONLY**
        - **HIRE DOCKET/ WORK ORDER NUMBER COLUMN CAN NEVER HAVE SINGLE DIGIT VALUES, FILL AS N/A IF IT DOES HAVE SINGLE DIGIT VALUES** 
     
        ---

        The context is as follows:
        {markdown_content}
        """

def get_both_prompt(markdown_content):
    """
    Returns the unified prompt for both invoice and timesheet data extraction.
    
    Args:
        markdown_content (str): The markdown content extracted from the PDF
        
    Returns:
        str: The unified prompt for processing
    """
    return f"""### Unified Prompt for Invoice and Timesheet Data Extraction
    
    #### **Identify Document Type**
    - Analyze the content to determine if the document is an **Invoice**, a **Timesheet**, or both.
    - IF ITS ONLY A TIMESHEET ONLY INCLUDE TIMESHEETS'S DEFINED PARAMETERS(SET1 OR SET 2) IN THE FINAL OUTPUT
    - IF ITS ONLY AN INVOICE ONLY INCLUDE INVOICE'S DEFINED PARAMETERS IN THE FINAL OUTPUT
    - MAP THE VALUES TO THE DEFINED PARAMTERS AS PER THE DOCUMENT TYPE (INVOICE OR TIMESHEET)
    - IGNORE IF VALUES CANT BE MAPPED TO THE DEFINED PARAMETERS, DONT INCLUDE 
    - Extract relevant fields based on the identified document type.
    - Choose the most suitable timesheet data extraction set with the most complete or accurate information.
    ---

    ### **Invoice Data Extraction** (include as title )

    ####  Invoice Header Information**
    - Invoice Number
    - Invoice Date
    - Invoice Terms
    - Due Date
    - Page Number

    ####  Company Details**
    - Company Name
    - Company Address
    - Company Phone Number	
    - Company Mobile Number
    - Company Email

    ####  Client Details**
    - Client Name
    - Client Address

    ####  Invoice Line Items** (this may have multiple records. The following are the headers of the table and the multiple records should be as rows in the table)
    - Job Order No
    - Purchase Order No
    - Payee Name
    - Weekending Date
    - Description
    - Item
    - Quantity
    - Rate
    - Invoice Amount (ex. Tax)

    ####  Bank Details**
    - Bank Name
    - BSB (Bank-State-Branch)
    - Account Number

    ####  Invoice Totals**
    - Sub Total
    - GST
    - Total Amount

    ---
    ### **Timesheet Data Extraction** *(include as title)*
    **INSTRUCTION**

    - The timesheet follows either **Set 1** or **Set 2** format. Choose the most suitable set based on the **context**.
    - **ONLY include the defined parameters from Set 1 or Set 2** in the final output.  
    - **Map values from the content (tables and text) to the defined parameters only.**
    - **Ignore unmapped values** — do **not** include them.
    - **Extract relevant fields based on the context**.
    - Choose the **most complete and accurate** timesheet data extraction set.
    - The context provided could be from a **single timesheet** or **multiple timesheets**.

    #### **IMPORTANT for MULTIPLE TIMESHEETS:**
    - If the content contains **a series of timesheets**, ensure that **each timesheet is distinctly identified**.
    - However, distinctly identify the rows from different timesheets in the output, include the **Employee Name** and **Date** (from the same page) **in each corresponding record/row** to maintain clarity.
    - This distinction can be made by referring to the **page number or section header in the context**.
    - Ensure that **all records grouped in a table share the same Employee Name and Date values from their respective page/context**.

    ### **IMPORTANT FOR TIME SHEETS**
    - When a single column in a row is filled add it to the previous row
    -Likewise when more than one column is filled in a single row  ADD IT AS A NEW ROW TO THE TABLE

    ---

    ### **Timesheet Data Extraction** *(include as title)*

    - Choose **Set 1** or **Set 2** based on completeness or accuracy of data.
    - **Do not mention "Set 1" or "Set 2"** in the final JSON output or markdown table.

    #### **Set 1: Extract Timesheet Header Information**
    - Payee No  
    - Payee Name  
    - Job Order  
    - Job Description  
    - Client Number  
    - Client Name  
    - Weekending Date  

    ####  Timesheet Attendance Details**
    - Date  
    - Start Time  
    - End Time  
    - Attendance/Absence Type  
    - Total Hours  

    ####  Additional Items**
    - Date  
    - Item Description  
    - Quantity  

    ####  Reimbursement Comments**
    - Comment Date  
    - Created Date & Time  
    - Created By  
    - Comment  
    - Display to Candidate (Yes/No)  
    - Display to Client Contact (Yes/No)  

    ####  Timesheet Totals**
    - Total Scheduled Hours  
    - Total Attendance Hours  
    - Total Absence Hours  

    ---

    #### **Set 2: Employee Details**
    *(If the timesheet follows this format, render each section (####) as a separate markdown table)*

    - Employee Name  
    - Employee Code *(Only if not "Crane logistics" or "EWP")*  
    - Type *(Crane logistics or EWP)*  
    - Depot  
    - Date  
    - Day *(Predict the day from the date parameter value and map it to the day parameter use Zeller’s Congruence if needed to find out the day)*

    #### **Allowances (KM's Section)**
    - Employee Name 
    - Date
    - KM's Allowance 1 *(with checkbox and description)*  
    - KM's Allowance 2 *(with checkbox and description)*  

    #### **Location Details**
    - Employee Name 
    - Date
    - Starting Location  
    - End Location  

    #### **Compliance Checks**
    - Employee Name 
    - Date
    - 10-Hour Break Since Last Shift (YES/NO)   
    - Lunch Break Taken (YES/NO)  
    - Next Shift 10-Hour Break Compliance (YES/NO) 
    - Incident/Injury Occurred (YES/NO, with incident report if YES) 

    #### **Shift Details Table**
    *("Description" can have multiple records; extract each record as a separate row. The following are the headers for this table)*
    *(if empty , fill N/A)*
    *(the 11th column should only be mapped to ASSET NO, And the value in the column before the customer name should be mapped to the HIREDOCKET COLUMN, Do not make any changes to other columns)
    - Employee Name 
    - Date
    - Start Time  
        - Values must be in HH:MM 24 hours format 
    - Finish Time  
        - Values must be in HH:MM 24 hours format 
    - Total Hours   
        - when start time and finish time is empty , fill total hours as N/A
    - Crane Operator *(checkbox)*  
        - map selected to YES and unselected to NO 
    - Rigger/Dogman *(checkbox)*  
        - map selected to YES and unselected to NO
    - Truck Driver *(checkbox)*  
        - map selected to YES and unselected to NO
    - Travel Tower Operator *(checkbox)* 
        - map selected to YES and unselected to NO
    - Mechanic *(checkbox)*  
        - map selected to YES and unselected to NO
    - Other *(checkbox)*  
        - map selected to YES and unselected to NO
    - Asset Number  
        - *(IMPORTANT: YOU MUST MAP THE VALUE FROM THE 11TH COLUMN IN THE TABLE TO THIS PARAMETER. DO NOT USE THIS VALUE FOR ASSET NUMBER)*
        - *(Enter ONLY genuine asset numbers in this field)*
        - *(Do NOT copy or duplicate the Hire Docket/Work Order Number into this field)*
        - *(If no distinct asset number is provided, leave this field blank or mark as "N/A")*
        -*(Donot map start time or finish time into this)*  
    - Hire Docket/Work Order Number  - (Values must be number only OR N/A) 
        *(IMPORTANT: YOU MUST MAP THE VALUE FROM THE 12TH COLUMN IN THE TABLE TO THIS PARAMETER. DO NOT USE THIS VALUE FOR ASSET NUMBER)*(The value in the column before Customer Name should be considered for Hire docket only applicable for this column dont make any changes to other columns, THIS IS ALWAYS APPLICABLE FOR EVERY ROW)
        **HIRE DOCKET/ WORK ORDER NUMBER COLUMN CAN NEVER HAVE SINGLE DIGIT VALUES, FILL AS N/A IF IT DOES HAVE SINGLE DIGIT VALUES**
    - Customer Name  
        - Values must be text only
    - Description  
        - Values must be text only , is a description of the job done for the day
    - Job Code  
        - ALWAYS FILL AS N/A
    - Job Complete (Y/N) 
        - map y to YES and n to NO 


    #### **Document Metadata**
    - Document Number (e.g., NAT-FM-PR-0109)  
    - Issue Date (e.g., 30/09/14)  

    ---

    ### **General Instructions**

    #### **Handle Multi-Page Documents**
    - Extract data from **all pages**, including headers, tables, and footers.

    #### **Validate Extracted Data**
    - Perform **cross-checks** for consistency and completeness.
    - **Ignore** missing or inconsistent fields.

    #### **Handle Checkboxes and Free-Text Fields**
    - Extract the selected **checkbox value (YES/NO)**.  
    - For **free-text fields** (e.g., descriptions, comments), extract the text as-is. If empty, ignore it.

    #### **Output Structured Data**
    - Output the extracted data as **well-structured markdown tables with appropriate field labels**.
    - **Only one set (Set 1 or Set 2)** should be selected and extracted per timesheet context.
    - Within the chosen set, **include only available fields**—**do not** leave empty cells or include missing fields.
    - **Do not include summary or extra explanations.**
    - **map selected to YES and unselected to NO** , there should be no cell with the values selected or unselected, if there is , they should be replaced with YES or NO respectively.
    - **Ensure markdown table formatting is valid**: headers, separators, and aligned cells must be used correctly.
    - **IMPORTANT** Remember to map the 12th column specifically to the Hire Docket/Work Order Number field, not to the Asset Number field.
    - **EXTREMELY IMPORTANT If only one column in a row is filled, merge its data with the previous row. If multiple columns are filled in a single row, add it as a new entry in the table.
    - ** INCLUDE THE COMPLIANCE CHECK TABLE ALSO FOR SET 2 IN TIMESHEET EXTRACTION 
    -**DONOT MAP THE START TIME, FINISH TIME INTO THE ASSET NUMBER.
    -**IF START TIME, FINISH TIME IS EMPTY OR N/A THE TOTAL HOURS SHOULD BE N/AFOR TIMESHEET EXTRACTION SET 2 ONLY**
    
    ---

    The context is as follows:
    {markdown_content}
    """
def get_multiple_timesheets_prompt(markdown_content):
    return f"""
        **GENERAL INSTRUCTION**

        - The timesheet follows either **Set 1** or **Set 2** format. Choose the most suitable set based on the **context**.
        - **ONLY include the defined parameters from Set 1 or Set 2** in the final output.  
        - **Map values from the content (tables and text) to the defined parameters only.**
        - **Ignore unmapped values** — do **not** include them.
        - **Extract relevant fields based on the context**.
        - Choose the **most complete and accurate** timesheet data extraction set.
        - The context provided could be from a **single timesheet** or **multiple timesheets**.

        #### **IMPORTANT for MULTIPLE TIMESHEETS:**
        - If the content contains **a series of timesheets**, ensure that **each timesheet is distinctly identified**.
        - However, distinctly identify the rows from different timesheets in the output, include the **Employee Name** and **Date** (from the same page) **in each corresponding record/row** to maintain clarity.
        - This distinction can be made by referring to the **page number or section header in the context**.
        - Ensure that **all records grouped in a table share the same Employee Name and Date values from their respective page/context**.

        ### **IMPORTANT FOR TIME SHEETS**
        - When a single column in a row is filled add it to the previous row
        -Likewise when more than one column is filled in a single row  ADD IT AS A NEW ROW TO THE TABLE
        - *(IMPORTANT: YOU MUST MAP THE VALUE FROM THE 12TH COLUMN IN THE TABLE TO HIRE DOCKET/WORK ORDER NO PARAMETER. DO NOT USE THIS VALUE FOR ASSET NUMBER)*(The value in the column before Customer Name should be considered for Hire docket only applicable for this column dont make any changes to other columns)
        - IMPORTANT **DO NOT map start time or finish time into HIRE DOCKET/WORK ORDER NO PARAMETER**

        ---

        ### **Timesheet Data Extraction** *(include as title)*

        - Choose **Set 1** or **Set 2** based on completeness or accuracy of data.
        - **Do not mention "Set 1" or "Set 2"** in the final JSON output or markdown table.

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
        *(If the timesheet follows this format, render each section (####) as a separate markdown table)*

        - Employee Name  
        - Employee Code *(Only if not "Crane logistics" or "EWP")*  
        - Type *(Crane logistics or EWP)*  
        - Depot  
        - Date  
        - Day *(Predict the day from the date parameter value and map it to the day parameter use Zeller’s Congruence if needed to find out the day)*

        #### **Allowances (KM's Section)**
        - Employee Name 
        - Date
        - KM's Allowance 1 *(with checkbox and description)*  
        - KM's Allowance 2 *(with checkbox and description)*  

        #### **Location Details**
        - Employee Name 
        - Date
        - Starting Location  
        - End Location  

        #### **Compliance Checks**
        - Employee Name 
        - Date
        - 10-Hour Break Since Last Shift (YES/NO)   
        - Lunch Break Taken (YES/NO)  
        - Next Shift 10-Hour Break Compliance (YES/NO) 
        - Incident/Injury Occurred (YES/NO, with incident report if YES) 

        #### **Shift Details Table**
        *("Description" can have multiple records; extract each record as a separate row. The following are the headers for this table)*
        *(if empty , fill N/A)*
        *(the 11th column should only be mapped to ASSET NO, And the value in the column before the customer name should be mapped to the HIREDOCKET COLUMN, Do not make any changes to other columns)
        - Employee Name 
        - Date
        - Start Time  
            - Values must be in HH:MM 24 hours format 
        - Finish Time  
            - Values must be in HH:MM 24 hours format 
        - Total Hours   
        - Crane Operator *(checkbox)*  
            - map selected to YES and unselected to NO 
        - Rigger/Dogman *(checkbox)*  
            - map selected to YES and unselected to NO
        - Truck Driver *(checkbox)*  
            - map selected to YES and unselected to NO
        - Travel Tower Operator *(checkbox)* 
            - map selected to YES and unselected to NO
        - Mechanic *(checkbox)*  
            - map selected to YES and unselected to NO
        - Other *(checkbox)*  
            - map selected to YES and unselected to NO
        - Asset Number  
            - *(IMPORTANT: YOU MUST MAP THE VALUE FROM THE 11TH COLUMN IN THE TABLE TO THIS PARAMETER. DO NOT USE THIS VALUE FOR ASSET NUMBER)*
            - *(Enter ONLY genuine asset numbers in this field)*
            - *(Do NOT copy or duplicate the Hire Docket/Work Order Number into this field)*
            - *(If no distinct asset number is provided, leave this field blank or mark as "N/A")*
            -*(Donot map start time or finish time into this)*
            

        - Hire Docket/Work Order Number  - (Values must be number only) 
            - *(IMPORTANT: YOU MUST MAP THE VALUE FROM THE 12TH COLUMN IN THE TABLE TO THIS PARAMETER. DO NOT USE THIS VALUE FOR ASSET NUMBER)*(The value in the column before Customer Name should be considered for Hire docket only applicable for this column dont make any changes to other columns, THIS IS ALWAYS APPLICABLE FOR EVERY ROW)
            -*(Donot map start time or finish time into this)*
            - LEAVE THE FIELD EMPTY IF THERE ARE NO CORRESPONDING VALUE IN THE CONTEXT.

        - Customer Name  
            - Values must be text only.
        - Description  
            - Values must be text only , is a description of the job done for the day
        - Job Code  
        - Job Complete (Y/N) 
            - map y to YES and n to NO 

        #### **Document Metadata**
        - Document Number (e.g., NAT-FM-PR-0109)  
        - Issue Date (e.g., 30/09/14)  

        ---

        ### **General Instructions**

        #### **Handle Multi-Page Documents**
        - Extract data from **all pages**, including headers, tables, and footers.

        #### **Validate Extracted Data**
        - Perform **cross-checks** for consistency and completeness.
        - **Ignore** missing or inconsistent fields.

        #### **Handle Checkboxes and Free-Text Fields**
        - Extract the selected **checkbox value (YES/NO)**.  
        - For **free-text fields** (e.g., descriptions, comments), extract the text as-is. If empty, ignore it.

        #### **Output Structured Data**
        - Output the extracted data as **well-structured markdown tables with appropriate field labels**.
        - **Only one set (Set 1 or Set 2)** should be selected and extracted per timesheet context.
        - Within the chosen set, **include only available fields**—**do not** leave empty cells or include missing fields.
        - **Do not include summary or extra explanations.**
        - **map selected to YES and unselected to NO** , there should be no cell with the values selected or unselected, if there is , they should be replaced with YES or NO respectively.
        - **Ensure markdown table formatting is valid**: headers, separators, and aligned cells must be used correctly.
        - **IMPORTANT** Remember to map the 12th column specifically to the Hire Docket/Work Order Number field, not to the Asset Number field,THIS IS ALWAYS ** FOR EVERY ROW**, START TIME FINISH TIME VALUES SHOULD NOT BE MAPPED INTO THIS.
        - **EXTREMELY IMPORTANT If only one column in a row is filled, merge its data with the previous row. If multiple columns are filled in a single row, add it as a new entry in the table.
        - ** INCLUDE THE COMPLIANCE CHECK TABLE ALSO
        -**DONOT MAP THE START TIME, FINISH TIME INTO THE ASSET NUMBER.
        -
     
        ---

        The context is as follows:
        {markdown_content}
        """
def get_prompt_by_type(document_type, markdown_content):
    """
    Get the appropriate prompt based on document type.
    
    Args:
        document_type (str): The type of document ('invoice', 'timesheet', or 'both')
        markdown_content (str): The markdown content extracted from the PDF
        
    Returns:
        str: The prompt for processing
    """
    if document_type == "Invoice":
        return get_invoice_prompt(markdown_content)
    elif document_type == "Timesheet":
        return get_timesheet_prompt(markdown_content)
    elif document_type == "Multiple Timesheets":
        return get_multiple_timesheets_prompt(markdown_content)
    else:  # 'both' or any other value
        return get_both_prompt(markdown_content)