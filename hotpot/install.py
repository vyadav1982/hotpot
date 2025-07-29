import click
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
from frappe.desk.page.setup_wizard.setup_wizard import add_all_roles_to, make_records


def after_install():
	print("Setting up Hotpot...")
	add_all_roles_to("Administrator")
	create_employee_custom_fields()
	create_property_setters()
	click.secho("Thank you for installing Hotpot!", fg="green")
	# create_meal_custom_fields()


def create_employee_custom_fields():
	create_custom_fields(
		{
			"Employee": [
				{
					"label": ("Band"),
					"fieldname": "band",
					"fieldtype": "Link",
					"options": "Employee Band",
					"insert_after": "branch",
				},
			]
		}
	)


def create_property_setters():
	make_property_setter(
		"Employee",
		"branch",
		"reqd",
		1,
		"Check",
	)
	# make_property_setter("Employee", "branch", "fieldtype", "Int", "Data")

	make_property_setter(
		"Employee",
		"department",
		"reqd",
		1,
		"Check",
	)


# def create_meal_custom_fields():
# 	create_custom_fields(
# 		{
# 			"Hotpot Meal": [
# 				{
# 					"label": ("Coupons"),
# 					"fieldname": "coupons",
# 					"fieldtype": "Data",
# 					"insertafter": "vendor_id",
# 				},
# 				{
# 					"label": ("Ratings"),
# 					"fieldname": "ratings",
# 					"fieldtype": "Data",
# 					"insertafter": "vendor_id",
# 				},
# 			]
# 		}
# 	)
