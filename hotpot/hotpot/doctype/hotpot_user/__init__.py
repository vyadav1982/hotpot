import frappe

def get_all_vendor(self):
    users = frappe.get_all("Hotpot User", 
        filters={"role": "Hotpot Vendor"}, 
    )
    return [[r.name, r.mrname] for r in users]