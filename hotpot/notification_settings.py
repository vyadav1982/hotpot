import frappe
from frappe.desk.doctype.notification_settings.notification_settings import NotificationSettings


class CustomNotificationSettings(NotificationSettings):
	def has_permission(self, ptype="read", user=None):
		user = user or frappe.session.user

		if user == "Administrator":
			return True

		if any(role in frappe.get_roles(user) for role in ["System Manager", "Hotpot Admin", "Hotpot HR"]):
			return self.name != "Administrator"

		return self.name == user
