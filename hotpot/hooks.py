app_name = "hotpot"
app_title = "Hotpot"
app_publisher = "Bytepanda Technologies Pvt. Ltd."
app_description = "Food Coupon App"
app_email = "info@bytepanda.in"
app_license = "unlicense"
app_logo = "/assets/hotpot/manifest/icon-512x512.png"
app_logo_url = "/assets/hotpot/manifest/icon-512x512.png"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
add_to_apps_screen = [
	{
		"name": "hotpot",
		"logo": "/assets/hotpot/manifest/Hotpot.png",
		"title": "Hotpot",
		"route": "/hotpot",
		"has_permission": "hotpot.permissions.check_app_permission",
	}
]

extend_bootinfo = "hotpot.boot.boot_session"

fixtures = [
	# "Module Profile",
	# "Hotpot Locations",
	# "Block Module",
	# {"doctype": "Report", "filters": {"module": ["=", "Hotpot"]}},
	{
		"doctype": "Role",
		"filters": {
			"name": [
				"in",
				[
					"Hotpot Admin",
					"Hotpot User",
					"Hotpot Server",
					"Hotpot Vendor",
					"Hotpot HR",
					"Hotpot Finance",
				],
			]
		},
	},
	{
		"doctype": "Custom DocPerm",
		"filters": {
			"role": [
				"in",
				[
					"Hotpot Admin",
					"Hotpot User",
					"Hotpot Server",
					"Hotpot Vendor",
					"Hotpot HR",
					"Hotpot Finance",
				],
			],
		},
	},
	{
		"doctype": "Role Permission for Page and Report",
		"filters": {
			"set_role_for": "Report",
			"role": [
				"in",
				[
					"Hotpot Admin",
					"Hotpot User",
					"Hotpot Server",
					"Hotpot Vendor",
					"Hotpot HR",
					"Hotpot Finance",
				],
			],
		},
	},
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "hotpot.bundle.css"
app_include_js = "hotpot.bundle.js"
app_include_js = ["/assets/hotpot/js/navbar_customizations.js", "/assets/hotpot/js/route_guard.js"]

# app_include_js = "/assets/hotpot/js/data_import_list.js"


# website_path_resolver = "hotpot.utils.route_protection.protect_routes"

# include js, css files in header of web template
# web_include_css = "/assets/hotpot/css/hotpot.css"
# web_include_js = "/assets/hotpot/js/hotpot.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "hotpot/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Data Import": "public/js/data_import.js"}
doctype_list_js = {"Data Import": "public/js/data_import_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "hotpot/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "hotpot.utils.jinja_methods",
# 	"filters": "hotpot.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "hotpot.install.before_install"
after_install = "hotpot.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "hotpot.uninstall.before_uninstall"
after_uninstall = "hotpot.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "hotpot.utils.before_app_install"
# after_app_install = "hotpot.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "hotpot.utils.before_app_uninstall"
# after_app_uninstall = "hotpot.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "hotpot.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Hotpot Meal": "hotpot.hotpot.doctype.hotpot_meal.hotpot_meal.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Data Import": "hotpot.overrides.CustomDataImport",
	"Notification Settings": "hotpot.notification_settings.CustomNotificationSettings",
}

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"hotpot.tasks.all"
# 	],
# 	"daily": [
# 		"hotpot.tasks.daily"
# 	],
# 	"hourly": [
# 		"hotpot.tasks.hourly"
# 	],
# 	"weekly": [
# 		"hotpot.tasks.weekly"
# 	],
# 	"monthly": [
# 		"hotpot.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "hotpot.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "hotpot.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "hotpot.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["hotpot.utils.before_request"]
# after_request = ["hotpot.utils.after_request"]

# Job Events
# ----------
# before_job = ["hotpot.utils.before_job"]
# after_job = ["hotpot.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"hotpot.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# website_route_rules = [
# 	{"from_route": "/hotpot/<path:app_path>", "to_route": "app"},
# 	{"from_route": "/hotpot_mobile/<path:app_path>", "to_route": "app"},
# ]
