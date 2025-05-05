
import frappe
# from frappe.core.doctype.data_import.data_import import get_template
import openpyxl
from io import BytesIO
import base64

@frappe.whitelist()
def get_filtered_import_template(doctype):
    """Generate a template with only allowed fields for import"""
    # Get doctype metadata
    meta = frappe.get_meta(doctype)
    
    user_field = ["Employee ID","E Mail","Mobile no.","Employee Name","Role","Tag Id","Department","Date of Joining","Date Of Birth","Coupon Count","Location"]
    meal_field = ["Category", "Meal Title", "Meal Items", "Meal Date"]
    meal_item_field = ["Item Name"]
    roles = frappe.get_roles()
    if "Hotpot Vendor" not in roles:
        meal_field.append("Vendor Id")
        meal_item_field.append("Vendor Id")
    fields_to_include = []
    if doctype == "Hotpot User":
        fields_to_include = user_field
    elif doctype == "Hotpot Meal":
        fields_to_include = meal_field
    elif doctype == "Hotpot Meal Items":
        fields_to_include = meal_item_field

 
        
    output = BytesIO()
    wb = openpyxl.Workbook()
    ws = wb.active
    if(fields_to_include==[]):
        ws['A1'] =  f"You do not have permission to import {doctype}"
    ws.append(fields_to_include)

    wb.save(output)
    output.seek(0)
    excel_base64 = base64.b64encode(output.read()).decode()

    return {
        "file_content": excel_base64,
        "filename": f"{doctype} Import Template.xlsx"
    }

@frappe.whitelist()
def check_if_needs_filtering(doctype):
    """Check if a doctype needs its import template to be filtered"""
    doctypes_needing_filtering = [
        "User", 
        "Customer",
        "Employee",
        # Add your specific doctypes that need filtering
        "Your DocType Name"
    ]
    
    # Also check by module
    meta = frappe.get_meta(doctype)
    module_needs_filtering = meta.module in ["Your Module Name", "Another Module"]
    
    return {
        "needs_filtering": doctype in doctypes_needing_filtering or module_needs_filtering
    }