frappe.pages['meal-list'].on_page_load = function(wrapper) {
	frappe.call({
        method: "frappe.client.get_value",
        args: {
            doctype: "Hotpot User",
            filters: {
                email: frappe.session.user
            },
            fieldname: "name"
        },
        callback: function(response) {
            if (response.message) {
                let vendor_id = response.message.name;
                window.location.href = `/app/hotpot-meal?is_deleted=0&vendor_id=${vendor_id}`;
            } else {
                frappe.msgprint("Vendor not found.");
            }
        }
    });
}