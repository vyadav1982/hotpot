# Copyright (c) 2024, Bytepanda Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

def set_user_password(site, user, password, logout_all_sessions=False):
	from frappe.utils.password import update_password
	
	print("##"*10,site,user,password)

	if not password:
		raise ValueError("Password cannot be empty.")

	try:
		frappe.init(site)
		frappe.connect()

		if not frappe.db.exists("User", user):
			print(f"User {user} does not exist")
			return

		update_password(user=user, pwd=password, logout_all_sessions=logout_all_sessions)
		frappe.db.commit()
	finally:
		frappe.destroy()

class HotpotUser(Document):
	def after_insert(self):
		try:
			if not frappe.db.exists("User", {"email": self.email}):
				names = self.employee_name.split(" ", 1)
				new_user = frappe.new_doc("User")
				new_user.update({
					"email": self.email,
					"first_name": names[0],
					"username": self.employee_id,
					"last_name": names[1] if len(names) > 1 else "",
					"enabled": 1,
					"document_follow_notify": 1,
					"follow_liked_documents": 1,
					"search_bar": 0,
					"default_app": "hotpot",
				})

				if not frappe.db.exists("Role", self.role):
					raise ValueError(f"Role {self.role} does not exist.")

				new_user.append_roles(self.role)
				new_user.flags.ignore_permissions = True
				new_user.flags.ignore_if_duplicate = True
				new_user.insert(ignore_permissions=True)
				new_user.reload()

				frappe.db.commit()
				set_user_password(frappe.local.site, self.email, self.password)
			else:
				frappe_user = self.email
		except frappe.ValidationError as e:
			frappe.log_error(f"User creation error: {e}")
			return {"status": "error", "message": "Failed to create user in Frappe"}
		except Exception as e:
			frappe.log_error(frappe.get_traceback(), "Unexpected error during user creation")
			return {"status": "error", "message": "An unexpected error occurred."}
