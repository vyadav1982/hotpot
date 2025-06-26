import os
import re
from datetime import datetime, timedelta

import frappe
import openpyxl
from frappe.core.doctype.data_import.data_import import DataImport
from frappe.utils import getdate, nowdate, today

from hotpot.utils.utc_time import *


class CustomDataImport(DataImport):
	def start_import(self):
		if self.import_file:
			file_doc = frappe.get_doc("File", {"file_url": self.import_file})
			file_path = file_doc.get_full_path()

			if os.path.exists(file_path):
				if self.reference_doctype == "Hotpot User":
					self.modify_excel_file(file_path)
				if self.reference_doctype == "Employee":
					preview = super().get_preview_from_template(self.import_file, self.google_sheets_url)
					if preview:
						header_to_index = {}
						for i, col in enumerate(preview["columns"]):
							if isinstance(col, dict) and "header_title" in col:
								header_to_index[col["header_title"]] = i
						self.create_user(preview, header_to_index)

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
				"Company",
				"Employee Number",
				"User ID",
				"First Name",
				"Gender",
				"Date of Birth",
				"Date of Joining",
				"Location",
				"Status",
			]
			meal_fields = ["Category", "Meal Title", "Meal Items", "Meal Date", "Buffer Coupon Count"]
			meal_item_fields = ["Item Name"]
			holiday_field = ["Date", "Title", "Location"]
			roles = frappe.get_roles()
			if "Hotpot Vendor" not in roles:
				meal_fields.append("Vendor")
				meal_item_fields.append("Vendor")

			if self.reference_doctype == "Employee":
				expected_fields = user_fields
			elif self.reference_doctype == "Hotpot Meal":
				expected_fields = meal_fields
			elif self.reference_doctype == "Hotpot Meal Items":
				expected_fields = meal_item_fields
			elif self.reference_doctype == "Hotpot Holidays":
				expected_fields = holiday_field
			else:
				frappe.throw(
					f"Reference DocType '{self.reference_doctype}' is not allowed for custom import."
				)

			
			# Check for missing/extra fields
			missing = [col for col in expected_fields if col not in column_headers]
			extra = [
				col
				for col in column_headers
				if col and col not in expected_fields and not col.startswith("Sr.")
			]

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

			# if self.reference_doctype=="Employee":
			# 	print(header_to_index)
			# 	self.create_user(preview_data,header_to_index)
			# 	return

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
				elif self.reference_doctype == "Hotpot Meal":
					self.validate_hotpot_meal(preview_data, header_to_index)
				elif self.reference_doctype == "Hotpot Meal Items":
					self.validate_hotpot_meal_items(preview_data, header_to_index)

			return preview_data

		except Exception as e:
			frappe.log_error(f"Error in get_preview_from_template: {str(e)}")
			frappe.throw(f"Error processing import template: {str(e)}")
			return None

	def _process_date_fields(self, row, row_idx, header_to_index):
		try:
			date_fields = ["Date of Joining", "Date Of Birth", "Meal Date"]
			today = frappe.utils.getdate(frappe.utils.today())
			if isinstance(today, datetime):
				today = today.date()

			for date_field in date_fields:
				idx = header_to_index.get(date_field)
				if idx is not None and idx < len(row):
					value = row[idx]

					if value:
						parsed_date = frappe.utils.getdate(value)

						if not parsed_date:
							frappe.throw(
								f"Row {row_idx + 2}: Invalid date format or value in '{date_field}' (value: {value}). Expected format: YYYY-MM-DD."
							)

						if isinstance(parsed_date, datetime):
							parsed_date = parsed_date.date()
						if date_field == "Meal Date":
							if parsed_date < today:
								frappe.throw(
									f"Row {row_idx + 2}: '{date_field}' cannot be in the past (value: {value})."
								)

						row[idx] = parsed_date.strftime("%Y-%m-%d")

		except Exception as e:
			frappe.log_error(f"Error processing date fields: {str(e)}")
			raise

	def validate_hotpot_user(self, preview_data, header_to_index):
		"""Validate fields for Hotpot User imports."""
		try:
			today = frappe.utils.today()
			eighteen_years_ago = (datetime.now() - timedelta(days=18 * 365)).date()

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
					mobile_no = mobile_no.split(".")[0].strip()
					if mobile_no.startswith("+"):
						mobile_no = "+" + re.sub(r"\D", "", mobile_no[1:])
					else:
						mobile_no = re.sub(r"\D", "", mobile_no)
						if not mobile_no.startswith("91"):
							mobile_no = "+91" + mobile_no
						else:
							mobile_no = "+" + mobile_no
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
					errors.append(
						f"Row {row_num}: Role '{role}' is not a valid role. Allowed: {', '.join(allowed_roles)}"
					)

			if errors:
				frappe.throw("<br>".join(errors))
		except Exception as e:
			if not str(e).startswith("Row"):
				frappe.log_error(f"Error validating Hotpot User data: {str(e)}")
				frappe.throw(f"Error validating user data: {str(e)}")
			else:
				raise

	def validate_hotpot_meal(self, preview_data, header_to_index):
		"""Validate fields for Hotpot Meal imports."""
		try:
			errors = []

			for row_num, row in enumerate(preview_data["data"], start=2):
				if not isinstance(row, list):
					continue
				roles = frappe.get_roles()
				if "Hotpot Vendor" not in roles:
					vendor_id = (
						row[header_to_index.get("Vendor", -1)].strip()
						if header_to_index.get("Vendor") is not None
						else ""
					)
				else:
					vendor_id = frappe.db.get_value("Hotpot User", {"email": frappe.session.user}, "name")

				category = (
					row[header_to_index.get("Category", -1)].strip()
					if header_to_index.get("Category") is not None
					else ""
				)
				meal_items_raw = (
					row[header_to_index.get("Meal Items", -1)].strip()
					if header_to_index.get("Meal Items") is not None
					else ""
				)
				buffer_count = (
					row[header_to_index.get("Buffer Coupon Count", 0)]
					if header_to_index.get("Buffer Coupon Count") is not None
					else ""
				)
				if buffer_count < 0:
					errors.append(f"Row {row_num}: Buffer Coupon Count cannot be negative.")
					continue
				try:
					category_doc = frappe.db.get_value(
						"Hotpot Meal Category", {"name": category, "is_active": 1}, "*", as_dict=True
					)
					# print(category_doc)

					if not category_doc:
						errors.append(f"Row {row_num}: Category '{category}' not found or inactive.")
						continue
				except Exception as e:
					errors.append(f"Row {row_num}: Error fetching Category '{category}': {str(e)}")
					continue

				try:
					vendor_doc = frappe.db.get_value(
						"Hotpot User",
						{"name": vendor_id, "is_active": 1, "is_deleted": 0, "is_vendor": 1},
						"*",
						as_dict=True,
					)

					if not vendor_doc:
						errors.append(f"Row {row_num}: Vendor '{vendor_id}' not found, inactive, or deleted.")
						continue
				except Exception as e:
					errors.append(f"Row {row_num}: Error fetching Vendor '{vendor_id}': {str(e)}")
					continue

				entered_items = [item.strip() for item in meal_items_raw.split(",") if item.strip()]
				existing_items = frappe.get_all(
					"Hotpot Meal Items", filters={"vendor_id": vendor_id}, pluck="item_name"
				)
				existing_items_lower = set(ei.lower() for ei in existing_items)
				# print("existing_items_lower", existing_items_lower)
				missing_items = [item for item in entered_items if item.lower() not in existing_items_lower]

				if missing_items:
					errors.append(
						f"Row {row_num}: These meal items are not found for vendor '{vendor_id}': {', '.join(missing_items)}"
					)
					continue
				if self.import_file:
					file_doc = frappe.get_doc("File", {"file_url": self.import_file})
					file_path = file_doc.get_full_path()

					if os.path.exists(file_path):
						self.set_items_to_lower(file_path)

				field_mapping = {
					"start_time": "Start Time",
					"end_time": "End Time",
					"lead_time": "Lead Time",
					"cancellation_time": "Cancellation Time",
					"meal_rate": "Meal Weight",
				}
				if "Hotpot Vendor" in roles:
					field_mapping["vendor_id"] = "Vendor"

				for doc_field, import_field in field_mapping.items():
					if import_field not in header_to_index:
						header_to_index[import_field] = len(preview_data["columns"])
						new_index = len(preview_data["columns"])
						preview_data["columns"].append(
							{
								"index": new_index,
								"column_number": new_index + 1,
								"doctype": "Hotpot Meal",
								"header_title": import_field,
								"map_to_field": None,
								"date_format": None,
								"df": {
									"fieldtype": "Datetime"
									if "Time" in import_field
									else "Float",  # Adjust as needed
									"fieldname": doc_field,
									"label": import_field,
									"parent": "Hotpot Meal",
								},
								"skip_import": False,
								"warnings": [],
							}
						)
					field_idx = header_to_index[import_field]

					while len(row) <= field_idx:
						row.append("")

					value = category_doc.get(doc_field)
					row[field_idx] = value
					if import_field == "Vendor":
						row[field_idx] = vendor_id
			# print("Updated columns:", preview_data["columns"])
			# print("Updated row:", row)

			if errors:
				frappe.throw("<br>".join(errors))

		except Exception as e:
			if not str(e).startswith("Row"):
				frappe.log_error(f"Error validating Hotpot Meal data: {str(e)}")
				frappe.throw(f"Unexpected error during validation: {str(e)}")
			else:
				raise

	def validate_hotpot_meal_items(self, preview_data, header_to_index):
		print(self.as_dict())
		"""Validate fields for Hotpot Meal Items imports."""
		try:
			errors = []

			for row_num, row in enumerate(preview_data["data"], start=2):
				if not isinstance(row, list):
					continue

				roles = frappe.get_roles()
				vendor_doc = None
				if "Hotpot Vendor" not in roles:
					vendor_id = (
						row[header_to_index.get("Vendor", -1)].strip()
						if header_to_index.get("Vendor") is not None
						else ""
					)
				else:
					vendor_id = frappe.db.get_value("Hotpot User", {"email": frappe.session.user}, "name")

				try:
					vendor_doc = frappe.db.get_value(
						"Hotpot User",
						{"name": vendor_id, "is_active": 1, "is_deleted": 0, "is_vendor": 1},
						"*",
						as_dict=True,
					)

					if not vendor_doc:
						errors.append(f"Row {row_num}: Vendor '{vendor_id}' not found, inactive, or deleted.")
						continue
				except Exception as e:
					errors.append(f"Row {row_num}: Error fetching Vendor '{vendor_id}': {str(e)}")
					continue

				item_name = (
					row[header_to_index.get("Item Name", -1)].strip().lower()
					if header_to_index.get("Item Name") is not None
					else ""
				)

				if not item_name:
					errors.append(f"Row {row_num}: Item Name is missing.")
					continue
				if self.status != "Success":
					try:
						existing_items = frappe.get_all(
							"Hotpot Meal Items", filters={"vendor_id": vendor_id}, pluck="item_name"
						)
						existing_items_lower = set(ei.strip().lower() for ei in existing_items)

						if item_name in existing_items_lower:
							errors.append(
								f"Row {row_num}: Item '{item_name}' already exists for Vendor '{vendor_id}'."
							)
							continue
					except Exception as e:
						errors.append(f"Row {row_num}: Error checking existing items: {str(e)}")
						continue

				field_mapping = {}
				if "Hotpot Vendor" in roles:
					field_mapping["vendor_id"] = "Vendor"

				if "Hotpot Vendor" in roles:
					import_field = "Vendor"
					doc_field = "vendor_id"

				for doc_field, import_field in field_mapping.items():
					if import_field not in header_to_index:
						header_to_index[import_field] = len(preview_data["columns"])
						new_index = len(preview_data["columns"])
						preview_data["columns"].append(
							{
								"index": new_index,
								"column_number": new_index + 1,
								"doctype": "Hotpot Meal Items",
								"header_title": import_field,
								"map_to_field": None,
								"date_format": None,
								"df": {
									"fieldtype": "Datetime"
									if "Time" in import_field
									else "Float",  # Adjust as needed
									"fieldname": doc_field,
									"label": import_field,
									"parent": "Hotpot Meal Items",
								},
								"skip_import": False,
								"warnings": [],
							}
						)
					field_idx = header_to_index[import_field]

					while len(row) <= field_idx:
						row.append("")

					if import_field == "Vendor":
						row[field_idx] = f"{vendor_doc.full_name} ({vendor_doc.name})"

			if errors:
				frappe.throw("<br>".join(errors))

		except Exception as e:
			if not str(e).startswith("Row"):
				frappe.log_error(f"Error validating Hotpot Meal Items data: {str(e)}")
				frappe.throw(f"Unexpected error during validation: {str(e)}")
			else:
				raise

	def create_user(self, preview_data, header_to_index):
		for row_num, row in enumerate(preview_data["data"], start=2):
			email = row[header_to_index.get("User ID")].strip()
			first_name = row[header_to_index.get("First Name")].strip()

			if not email:
				frappe.throw("Email is required to create a user.")

			# Check if user already exists
			if not frappe.db.exists("User", email):
				user = frappe.get_doc(
					{
						"doctype": "User",
						"email": email,
						"first_name": first_name,
						"enabled": 1,
						"send_welcome_email": 1,
						"role_profile_name": "",
						"roles": [{"role": "Hotpot User"}],
					}
				)
				user.flags.ignore_permissions = True
				user.insert(ignore_if_duplicate=True)
				frappe.db.commit()
			# else:
			# frappe.msgprint(f"User '{email}' already exists.")

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
					mobile_no = mobile_no.split(".")[0].strip()
					if mobile_no.startswith("+"):
						# Remove non-digits after '+'
						mobile_no = "+" + re.sub(r"\D", "", mobile_no[1:])
					else:
						mobile_no = re.sub(r"\D", "", mobile_no)
						if not mobile_no.startswith("91"):
							mobile_no = "+91" + mobile_no
						else:
							mobile_no = "+" + mobile_no

					if mobile_no.startswith("+91") and len(mobile_no) == 13:
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

	def set_items_to_lower(self, file_path):
		try:
			wb = openpyxl.load_workbook(file_path)
			sheet = wb.active

			headers = [cell.value for cell in sheet[1]]
			header_to_index = {header.strip(): idx for idx, header in enumerate(headers) if header}

			meal_col_idx = header_to_index.get("Meal Items")
			if meal_col_idx is None:
				frappe.throw("Column 'Meal Items' not found in the Excel file.")

			category_col_idx = header_to_index.get("Category")
			if category_col_idx is None:
				frappe.throw("Column 'Category' not found in the Excel file.")

			for row_num, row in enumerate(sheet.iter_rows(min_row=2), start=2):
				cell = row[meal_col_idx]
				if cell.value:
					items = [item.strip().lower() for item in str(cell.value).split(",") if item.strip()]
					cell.value = ", ".join(items)

				cat_cell = row[category_col_idx]
				if cat_cell.value:
					original_val = cat_cell.value
					cat_cell.value = str(cat_cell.value).strip().lower()

			wb.save(file_path)

		except Exception as e:
			frappe.throw(f"Error processing Excel file: {str(e)}")
