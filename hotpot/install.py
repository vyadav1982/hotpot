import click
import frappe
from frappe.desk.page.setup_wizard.setup_wizard import add_all_roles_to, make_records


def after_install():
	print("Setting up Hotpot...")
	add_all_roles_to("Administrator")
	click.secho("Thank you for installing Hotpot!", fg="green")
