import click
import frappe
from frappe.desk.page.setup_wizard.setup_wizard import add_all_roles_to, make_records
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields



def after_install():
	print("Setting up Hotpot...")
	add_all_roles_to("Administrator")
	create_meal_custom_fields()
	click.secho("Thank you for installing Hotpot!", fg="green")


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