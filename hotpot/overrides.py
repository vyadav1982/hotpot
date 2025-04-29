import frappe
from frappe.core.doctype.data_import.data_import import DataImport
from datetime import datetime, timedelta
import re
import os
import openpyxl
from frappe.utils import getdate, today, nowdate


import openpyxl
import re
from frappe.utils import getdate, nowdate
import frappe


class CustomDataImport(DataImport):
	def start_import(self):
		if self.import_file:
			file_doc = frappe.get_doc("File", {"file_url": self.import_file})
			file_path = file_doc.get_full_path()
			
			if os.path.exists(file_path):
				print(f"File exists: {file_path}")
				self.modify_excel_file(file_path)
			
				
		return super().start_import()
	
	def get_preview_from_template(self, import_file=None, google_sheets_url=None):
		try:
			preview_data = super().get_preview_from_template(import_file, google_sheets_url)
			
			if not preview_data or not isinstance(preview_data, dict):
				return preview_data
				
			if "data" not in preview_data or "columns" not in preview_data:
				return preview_data
				
			column_headers = []
			if isinstance(preview_data["columns"], list):
				for col in preview_data["columns"]:
					if isinstance(col, dict) and "header_title" in col:
						column_headers.append(col["header_title"])
					elif isinstance(col, str):
						column_headers.append(col)
						
			# If we couldn't extract headers, return original data
			if not column_headers:
				return preview_data
				
			user_fields = [
				"Employee ID", "E Mail", "Mobile no.", "Employee Name", "Role",
				"Tag Id", "Department", "Date of Joining", "Date Of Birth",
				"Coupon Count", "Location"
			]
			meal_fields = [
				"Category", "Meal Title", "Meal Items", "Buffer Coupon Count",
				"Vendor Id", "Meal Date", "Meal Weight", "Is Special"
			]

			if self.reference_doctype == "Hotpot User":
				expected_fields = user_fields
			elif self.reference_doctype == "Hotpot Meal":
				expected_fields = meal_fields
			else:
				frappe.throw(f"Reference DocType '{self.reference_doctype}' is not allowed for custom import.")

			# Check for missing/extra fields
			missing = [col for col in expected_fields if col not in column_headers]
			extra = [col for col in column_headers if col not in expected_fields and not col.startswith("Sr.")]

			if missing or extra:
				error_msg = []
				if missing:
					error_msg.append(f"Missing columns: {', '.join(missing)}")
				if extra:
					error_msg.append(f"Extra columns: {', '.join(extra)}")
				frappe.throw("<br>".join(error_msg))

			# Create a mapping from header titles to column indices
			header_to_index = {}
			for i, col in enumerate(preview_data["columns"]):
				if isinstance(col, dict) and "header_title" in col:
					header_to_index[col["header_title"]] = i

			# Validate data rows
			if isinstance(preview_data["data"], list):
				for row_idx, row in enumerate(preview_data["data"]):
					# Handle each row safely
					if not isinstance(row, list):
						continue
						
					# Process date fields
					self._process_date_fields(row, row_idx, header_to_index)
				
				# Perform doctype-specific validation
				if self.reference_doctype == "Hotpot User":
					self.validate_hotpot_user(preview_data, header_to_index)

			return preview_data
			
		except Exception as e:
			frappe.log_error(f"Error in get_preview_from_template: {str(e)}")
			frappe.throw(f"Error processing import template: {str(e)}")
			return None

	def _process_date_fields(self, row, row_idx, header_to_index):
		"""Process date fields in a row safely"""
		try:
			date_fields = ["Date of Joining", "Date Of Birth"]
			for date_field in date_fields:
				idx = header_to_index.get(date_field)
				if idx is not None and idx < len(row):
					value = row[idx]
					if value and not isinstance(value, datetime):
						try:
							parsed_date = frappe.utils.getdate(value)
							row[idx] = parsed_date.strftime("%Y-%m-%d")
						except Exception:
							frappe.throw(f"Row {row_idx+2}: Invalid date format in '{date_field}'. Expected format: YYYY-MM-DD.")
		except Exception as e:
			frappe.log_error(f"Error processing date fields: {str(e)}")
			
	def validate_hotpot_user(self, preview_data, header_to_index):
		"""Validate fields for Hotpot User imports."""
		try:

			today = frappe.utils.today()
			eighteen_years_ago = (datetime.now() - timedelta(days=18*365)).date()

			allowed_roles = ["Hotpot Admin", "Hotpot User", "Hotpot Vendor", "Hotpot HR"]
			errors = []

			for row_num, row in enumerate(preview_data["data"], start=2):
				if not isinstance(row, list):
					continue

				doj_idx = header_to_index.get("Date of Joining", -1)
				dob_idx = header_to_index.get("Date Of Birth", -1)
				role_idx = header_to_index.get("Role", -1)
				mobile_no_idx = header_to_index.get("Mobile no.", -1)

				doj = row[doj_idx] if doj_idx >= 0 and doj_idx < len(row) else None
				dob = row[dob_idx] if dob_idx >= 0 and dob_idx < len(row) else None
				role = row[role_idx] if role_idx >= 0 and role_idx < len(row) else None
				mobile_no = row[mobile_no_idx] if mobile_no_idx >= 0 and mobile_no_idx < len(row) else None

				# Convert all values to strings for safe comparison
				role = str(role) if role is not None else None
				mobile_no = str(mobile_no) if mobile_no is not None else None

				# Validate Date of Joining
				if doj:
					try:
						doj_value = frappe.utils.getdate(doj)
						if doj_value > frappe.utils.getdate(today):
							errors.append(f"Row {row_num}: Date of Joining '{doj}' must be before today.")
					except Exception:
						errors.append(f"Row {row_num}: Invalid Date of Joining '{doj}'.")

				# Validate Mobile Number
				if mobile_no:
					mobile_no = mobile_no.strip()
					if mobile_no.startswith('+'):
						mobile_no = '+' + re.sub(r'\D', '', mobile_no[1:])
					else:
						mobile_no = re.sub(r'\D', '', mobile_no)
						if not mobile_no.startswith('91'):
							mobile_no = '+91' + mobile_no
						else:
							mobile_no = '+' + mobile_no
					row[mobile_no_idx] = mobile_no

				# Validate Date of Birth
				if dob:
					try:
						dob_value = frappe.utils.getdate(dob)
						if dob_value >= eighteen_years_ago:
							errors.append(f"Row {row_num}: Date of Birth '{dob}' indicates age less than 18.")
					except Exception:
						errors.append(f"Row {row_num}: Invalid Date of Birth '{dob}'.")

				# Validate Role
				if role and role not in allowed_roles:
					errors.append(f"Row {row_num}: Role '{role}' is not a valid role. Allowed: {', '.join(allowed_roles)}")

			if errors:
				frappe.throw("<br>".join(errors))
		except Exception as e:
			if not str(e).startswith("Row"):
				frappe.log_error(f"Error validating Hotpot User data: {str(e)}")
				frappe.throw(f"Error validating user data: {str(e)}")
			else:
				raise

				
	def modify_excel_file(self, file_path):
		try:
			wb = openpyxl.load_workbook(file_path)
			sheet = wb.active

			headers = [cell.value for cell in sheet[1]]
			header_map = {header: idx for idx, header in enumerate(headers)}

			# Required field names
			mobile_field = "Mobile no."
			errors = []

			for row_num, row in enumerate(sheet.iter_rows(min_row=2), start=2):
				mobile_cell = row[header_map[mobile_field]].value
				mobile_no = str(mobile_cell).strip() if mobile_cell else ""
				if mobile_no:
					mobile_no = mobile_no.strip()
					if mobile_no.startswith('+'):
						# Remove non-digits after '+'
						mobile_no = '+' + re.sub(r'\D', '', mobile_no[1:])
					else:
						mobile_no = re.sub(r'\D', '', mobile_no)
						if not mobile_no.startswith('91'):
							mobile_no = '+91' + mobile_no
						else:
							mobile_no = '+' + mobile_no

					if mobile_no.startswith('+91') and len(mobile_no) == 13:
						formatted_mobile = f"+91- {mobile_no[3:]}"
						row[header_map[mobile_field]].value = formatted_mobile
					else:
						row[header_map[mobile_field]].value = mobile_no
						errors.append(f"Row {row_num}: Unexpected mobile format '{mobile_no}'.")
				else:
					errors.append(f"Row {row_num}: Mobile number is missing.")
			print(f"Processed {len(sheet['A'])} rows.")
			wb.save(file_path)
			print("Excel file updated successfully.")

			if errors:
				frappe.throw("<br>".join(errors))
		except Exception as e:
			frappe.throw(f"Error processing Excel file: {str(e)}")
