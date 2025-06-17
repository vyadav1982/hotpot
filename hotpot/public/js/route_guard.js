const allowed_routes_by_role = {
	"Hotpot Admin": [
		"hotpot",
		"user",
		"employee",
		"employee-health-insurance",
		"designation",
		"branch",
		"employee-grade",
		"department",
		"employement-type",
		"job-applicant",
		"holiday-list",
		"cost-center",
		"hotpot-meal",
		"hotpot-draft-meal",
		"hotpot-user",
		"hotpot-meal-items",
		"hotpot-holidays",
		"hotpot-meal-category",
		"hotpot-meal-types",
		"query-report/guest-meal-consumption-report",
		"query-report/birthday-coupons-report",
		"query-report/joining-day-coupons-report",
		"query-report/meal-consumption-report",
		'query-report/coupon-report',
		'query-report/employee-wise-meal-amount',
		"hotpot-approvals",
		"hotpot-configurations",
		"generate-guest-qr",
		'load-wallet-balance',
		"data-import",
	],
	"Hotpot HR": [
		"hotpot-hr",
		"hotpot-user",
		"hotpot-holidays",
		"query-report/guest-meal-consumption-report",
		"query-report/birthday-coupons-report",
		"query-report/joining-day-coupons-report",
		"query-report/meal-consumption-report",
		'query-report/coupon-report',
		'query-report/employee-wise-meal-amount',
		"hotpot-approvals",
		"hotpot-draft-meal",
		'load-wallet-balance',
	],
	"Hotpot Finance": [
		"hotpot-finance",
		"query-report/guest-meal-consumption-report",
		"query-report/birthday-coupons-report",
		"query-report/joining-day-coupons-report",
		"query-report/meal-consumption-report",
		'query-report/coupon-report',
		'query-report/employee-wise-meal-amount',
	],
	"Hotpot Vendor": [
		"hotpot-vendor",
		"data-import",
		"meal-list",
		"hotpot-meal",
		"hotpot-meal-items",
		"meal-item-list",
		'query-report/coupon-report',
	],
};

const common_whitelist = ["home", "desk", "app", "login"];

// Safer route string getter that doesn't depend solely on frappe._route
function getRouteStr() {
	// First try Frappe's built-in function - this is the most reliable
	if (frappe.get_route_str && typeof frappe.get_route_str === "function") {
		const routeStr = frappe.get_route_str();
		if (routeStr) {
			//console.log("Route detected via frappe.get_route_str():", routeStr);
			return routeStr;
		}
	}

	// Try to get route from frappe.get_route()
	if (frappe.get_route && typeof frappe.get_route === "function") {
		const route = frappe.get_route();
		if (Array.isArray(route) && route.length) {
			//console.log("Route detected via frappe.get_route():", route.join("/"));
			return route.join("/");
		}
	}

	// Try to get route from other Frappe properties
	if (frappe._cur_route) {
		const routeStr = Array.isArray(frappe._cur_route)
			? frappe._cur_route.join("/")
			: frappe._cur_route;
		//console.log("Route detected via frappe._cur_route:", routeStr);
		return routeStr;
	}

	if (frappe._route && Array.isArray(frappe._route) && frappe._route.length) {
		//console.log("Route detected via frappe._route:", frappe._route.join("/"));
		return frappe._route.join("/");
	}

	// Check if we can extract from page_name
	if (frappe.current_page && frappe.current_page.page_name) {
		//console.log("Route detected via page_name:", frappe.current_page.page_name);
		return frappe.current_page.page_name;
	}

	// Fallback to window location
	const hash = window.location.hash.replace("#", "");
	if (hash) {
		//console.log("Route detected via window.location.hash:", hash);
		return hash;
	}

	const path = window.location.pathname.replace(/^\/+|\/+$/g, "");
	//console.log("Route detected via window.location.pathname:", path);
	return path;
}

function normalizeRoute(route) {
	if (!route) return "";

	route = route.toLowerCase().trim();

	// Handle Workspace routes specifically (e.g. "Workspaces/Hotpot Workspace" → "hotpot-workspace")
	if (route.toLowerCase().startsWith("workspaces/")) {
		const workspaceName = route.split("/")[1] || "";
		return workspaceName
			.toLowerCase()
			.replace(/\s+/g, "-")
			.replace(/[^\w-]+/g, "");
	}

	// Handle query reports
	if (route.startsWith("query-report/")) {
		return route.replace(/\s+/g, "-").replace(/[^\w/-]+/g, "");
	}

	const parts = route.split("/");
	const main = parts.length > 1 ? parts[1] : parts[0];
	return main.replace(/\s+/g, "-").replace(/[^\w-]+/g, "");
}

function isRouteAllowed(route) {
	if (!route) return true;
	const user_roles = frappe?.boot?.user?.roles || [];
	if (
		user_roles.includes("HR Manager") ||
		user_roles.includes("HR User") ||
		user_roles.includes("Employee")
	) {
		return true;
	}

	if (user_roles.includes("Hotpot Vendor") && route == "data-import/new-data-import") {
		return true;
	}
	const normalized = normalizeRoute(route);
	if (user_roles.includes("Administrator")) {
		//console.log("✅ User is Administrator — full access granted");
		return true;
	}
	// if (user_roles.includes("Hotpot Vendor") && route.includes("List")) {
	//     return false;
	// }
	// Allow common routes
	if (common_whitelist.includes(normalized)) {
		return true;
	}

	// Check role-based permissions
	for (const role of Object.keys(allowed_routes_by_role)) {
		if (user_roles.includes(role)) {
			const allowed_routes = allowed_routes_by_role[role];
			if (allowed_routes.includes(normalized)) {
				//console.log(`✅ Access granted to "${normalized}" for role: ${role}`);
				return true;
			}
		}
	}

	//console.log(`⛔ Access denied to "${normalized}"`);
	return false;
}

function getDefaultWorkspace() {
	const roles = frappe?.boot?.user?.roles || [];
	if (roles.includes("Hotpot Admin")) return "hotpot";
	if (roles.includes("Hotpot HR")) return "hotpot-hr";
	if (roles.includes("Hotpot Finance")) return "hotpot-finance";
	if (roles.includes("Hotpot Vendor")) return "hotpot-vendor";
	return "home";
}

// Authorization state variables
let pendingRedirect = null;
let isMessageDisplayed = false;
let redirectAttempts = 0;
let authCheckInProgress = false;

function blockIfUnauthorized() {
	if (authCheckInProgress) return;
	authCheckInProgress = true;

	try {
		const route = getRouteStr();
		if (!route) {
			resetAuthorizationState();
			authCheckInProgress = false;
			return;
		}

		//console.log("🔍 Checking access for route:", route);
		const normalized = normalizeRoute(route);
		//console.log("Normalized to:", normalized);

		if (common_whitelist.includes(normalized) || pendingRedirect === route) {
			//console.log("Route is whitelisted or pending redirect");
			resetAuthorizationState();
			authCheckInProgress = false;
			return;
		}

		// Get the actual DOM content to verify we're checking the right page
		const pageTitle = document.title || "";
		const visibleContent = $(".page-container").text().substring(0, 100);
		//console.log("Current page appears to be:", pageTitle, "Content preview:", visibleContent);

		if (!isRouteAllowed(route)) {
			//console.log("⛔ Access denied to route:", route);

			// Check if we're on a doctype page specifically
			const isDoctypePage =
				route.toLowerCase().includes("doctype") ||
				pageTitle.toLowerCase().includes("doctype") ||
				visibleContent.toLowerCase().includes("doctype");

			if (isDoctypePage) {
				//console.log("Detected unauthorized doctype page");
			}

			if (!isMessageDisplayed) {
				frappe.msgprint({
					title: "Access Denied",
					indicator: "red",
					message: "⛔ You are not allowed to access this page.",
				});
				isMessageDisplayed = true;
			}

			const fallback = getDefaultWorkspace();
			//console.log("Redirecting to fallback:", fallback);

			if (route !== fallback && normalizeRoute(route) !== fallback) {
				pendingRedirect = fallback;

				// Force reload if content doesn't match route (handles stale content)
				if (isDoctypePage) {
					//console.log("Forcing page reload to clear doctype content");
					window.location.href = window.location.origin + "/app/" + fallback;
					authCheckInProgress = false;
					return;
				}

				setTimeout(() => {
					frappe.set_route(fallback);
					authCheckInProgress = false;
				}, 300);
			} else {
				authCheckInProgress = false;
			}
		} else {
			//console.log("✅ Access granted to route:", route);
			resetAuthorizationState();
			authCheckInProgress = false;
		}
	} catch (e) {
		//console.error("Error in blockIfUnauthorized:", e);
		authCheckInProgress = false;
	}
}

// Override Route with safety checks
const original_set_route = frappe.set_route;

frappe.set_route = function (...args) {
	try {
		const target =
			args.length > 1
				? args.join("/")
				: typeof args[0] === "string"
				? args[0]
				: Array.isArray(args[0])
				? args[0].join("/")
				: "";

		redirectAttempts++;

		if (redirectAttempts > 5) {
			//console.error("🚨 Too many redirects, routing to home.");
			resetAuthorizationState();
			return original_set_route("app");
		}

		if (pendingRedirect && target !== pendingRedirect) {
			//console.log("🔁 Redirecting to authorized route:", pendingRedirect);
			const result = original_set_route(pendingRedirect);
			setTimeout(() => (redirectAttempts = 0), 500);
			return result;
		}

		if (isRouteAllowed(target)) {
			resetAuthorizationState();
		}

		const result = original_set_route.apply(this, args);
		setTimeout(blockIfUnauthorized, 200);
		return result;
	} catch (e) {
		//console.error("Error in set_route override:", e);
		resetAuthorizationState();
		return original_set_route.apply(this, args);
	}
};

function resetAuthorizationState() {
	pendingRedirect = null;
	isMessageDisplayed = false;
	redirectAttempts = 0;
}

// Set up route change handler
function setupRouteChangeHandler() {
	if (frappe.router && typeof frappe.router.on === "function") {
		frappe.router.on("change", () => {
			setTimeout(() => {
				try {
					const route_str = getRouteStr();
					const normalized = normalizeRoute(route_str);

					if (!route_str || common_whitelist.includes(normalized)) return;

					if (!isRouteAllowed(route_str)) {
						frappe.msgprint({
							title: "Access Denied",
							indicator: "red",
							message: "⛔ You are not allowed to access this page.",
						});

						const fallback = getDefaultWorkspace();
						setTimeout(() => frappe.set_route(fallback), 300);
					}
				} catch (e) {
					//console.error("Error in route change handler:", e);
				}
			}, 100);
		});
	}
}

// Safe initialization
$(document).ready(() => {
	try {
		resetAuthorizationState();

		// Check authorization after DOM is ready
		setTimeout(() => {
			blockIfUnauthorized();

			// Add click handler for anchor links
			$(document).on("click", 'a[href^="#"]', () => {
				setTimeout(resetAuthorizationState, 200);
				setTimeout(blockIfUnauthorized, 300);
			});
		}, 500);
	} catch (e) {
		//console.error("Error in document ready handler:", e);
	}
});

// Set up route change handler after Ajax completes
$(document).on("frappe.after_ajax", function () {
	try {
		setupRouteChangeHandler();
		setTimeout(blockIfUnauthorized, 200);
	} catch (e) {
		//console.error("Error in after_ajax handler:", e);
	}
});

// Alternative method to hook into Frappe's ready event
if (frappe.ready) {
	frappe.ready(() => {
		setupRouteChangeHandler();
		setTimeout(blockIfUnauthorized, 300);
	});
}

// Handle content loaded after page navigation
$(document).on("page-change", function () {
	//console.log("Page change detected");
	setTimeout(blockIfUnauthorized, 100);
});

// Deep integration with Frappe's router events
if (frappe.router) {
	// Override the show_not_found method
	const original_show_not_found = frappe.router.show_not_found;
	frappe.router.show_not_found = function () {
		// Before showing 404, check if this is an authorization issue
		const currentRoute = getRouteStr();
		if (currentRoute && !isRouteAllowed(currentRoute)) {
			//console.log("Caught unauthorized 404 attempt:", currentRoute);
			frappe.set_route(getDefaultWorkspace());
			return;
		}
		return original_show_not_found.apply(this, arguments);
	};

	// Handle history state changes (back/forward navigation)
	$(window).on("popstate", function () {
		setTimeout(blockIfUnauthorized, 100);
	});
}

// Intercept page rendering
const originalRender = frappe.render_template;
if (originalRender && typeof originalRender === "function") {
	frappe.render_template = function (template_name, context, is_jinja) {
		const result = originalRender.apply(this, arguments);

		// After any template renders, check authorization
		setTimeout(function () {
			blockIfUnauthorized();
		}, 0);

		return result;
	};
}

// Detect and handle doctype pages specifically
function checkForDoctypeContent() {
	// Look for doctype-specific elements
	const hasDoctypeElements =
		$(".doctype-actions").length > 0 ||
		$(".doctype-row").length > 0 ||
		$("[data-doctype]").length > 0;

	if (hasDoctypeElements) {
		//console.log("Doctype elements detected in DOM");
		const currentRoute = getRouteStr();
		if (!isRouteAllowed(currentRoute)) {
			//console.log("Forcing redirect from unauthorized doctype page");
			frappe.set_route(getDefaultWorkspace());
		}
	}
}

// Run checks periodically to catch any issues
setInterval(function () {
	checkForDoctypeContent();
}, 2000);

// For debugging
window.debugRouteAuth = {
	getRoute: getRouteStr,
	checkAccess: isRouteAllowed,
	reset: resetAuthorizationState,
};
