import click
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.desk.page.setup_wizard.setup_wizard import add_all_roles_to, make_records
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def after_install():
	print("Setting up Hotpot...")
	add_all_roles_to("Administrator")
	create_employee_custom_fields()
	create_property_setters()
	click.secho("Thank you for installing Hotpot!", fg="green")
	create_meal_custom_fields()


def create_employee_custom_fields():
	create_custom_fields(
		{
			"Employee": [
				{
					"label": ("Band"),
					"fieldname": "band",
					"fieldtype": "Link",
					"options":"Employee Band",
					"insert_after": "branch",
				},
				
				{
					"label": ("Location"),
					"fieldname": "location",
					"fieldtype": "Link",
					"options":"Company Locations",
					"insert_after": "band",
				},
				
			]
		}
	)

# def create_property_setters():

# 	frappe.make_property_setter(
# 		"Employee",
# 		"location",
# 		"reqd",
# 		1, 
# 		"Check",
# 	)
# 	frappe.make_property_setter(
# 		"Employee",
# 		"branch",
# 		"hidden",
# 		1,
# 		"Check",
# 	)
# 	frappe.make_property_setter(
# 		"Employee",
# 		"branch",
# 		"reqd",
# 		0,
# 		"Check",
# 	)
# 	frappe.make_property_setter(
# 		"Employee",
# 		"department",
# 		"reqd",
# 		1,
# 		"Check",
# 	)


def create_property_setters():
	frappe.get_doc({
		"doctype": "Property Setter",
		"doc_type": "Employee",
		"doctype_or_field": "DocField",
		"field_name": "location",
		"property": "reqd",
		"value": 1,
		"property_type": "Check"
	}).insert()

	frappe.get_doc({
		"doctype": "Property Setter",
		"doc_type": "Employee",
		"doctype_or_field": "DocField",
		"field_name": "department",
		"property": "reqd",
		"value": 1,
		"property_type": "Check"
	}).insert()

	frappe.get_doc({
		"doctype": "Property Setter",
		"doc_type": "Employee",
		"doctype_or_field": "DocField",
		"field_name": "branch",
		"property": "hidden",
		"value": 1,
		"property_type": "Check"
	}).insert()

	frappe.get_doc({
		"doctype": "Property Setter",
		"doc_type": "Employee",
		"doctype_or_field": "DocField",
		"field_name": "branch",
		"property": "reqd",
		"value": 0,
		"property_type": "Check"
	}).insert()

	frappe.db.commit()


def create_meal_custom_fields():
	
	create_custom_fields(
		{
			"Hotpot Meal": [
				{
					"label": ("Coupons"),
					"fieldname": "coupons",
					"fieldtype": "Data",
					"insertafter": "vendor_id",
				},
				{
					"label": ("Ratings"),
					"fieldname": "ratings",
					"fieldtype": "Data",
					"insertafter": "vendor_id",
				},
			]
		}
	)
