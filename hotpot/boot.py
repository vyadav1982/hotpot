import frappe
import sentry_sdk
from frappe import get_site_config
from sentry_sdk.integrations.excepthook import ExcepthookIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

sentry_dsn = get_site_config().get("sentry_dsn")

sentry_sdk.init(
	dsn=sentry_dsn,
	integrations=[LoggingIntegration(level=None, event_level="ERROR"), ExcepthookIntegration()],
	traces_sample_rate=1.0,
	send_default_pii=True,
)


def boot_session(bootinfo):
	bootinfo.show_hotpot_on_desk = True
