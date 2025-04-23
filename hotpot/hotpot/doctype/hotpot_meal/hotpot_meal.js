frappe.ui.form.on("Hotpot Meal", {
    refresh: function(frm) {
        const userRoles = frappe.user_roles;
        const grid = frm.fields_dict.coupons.grid;
        
        
        const disableGear = () => grid.wrapper.find('use[href="#icon-setting-gear"]').closest('a').hide().off('click');
        grid.wrapper.find('.col.grid-static-col.d-flex.justify-content-center').css({'pointer-events': 'none', 'cursor': 'default'}).off('click');
        if (!userRoles.includes('Hotpot Admin')) {
            grid.wrapper.find('.grid-row').css('pointer-events', 'none');
            grid.wrapper.find('.btn-open-row').hide();
            frm.fields.forEach(function(field) {
                if (!['Section Break', 'Column Break', 'Table'].includes(field.df.fieldtype)) {
                    frm.set_df_property(field.df.fieldname, 'read_only', 1);
                }
            });
            setTimeout(disableGear, 0);
        }
        const grid2 = frm.fields_dict.ratings.grid;
        
        
        const disableGear2 = () => grid2.wrapper.find('use[href="#icon-setting-gear"]').closest('a').hide().off('click');
        grid2.wrapper.find('.col.grid-static-col.d-flex.justify-content-center').css({'pointer-events': 'none', 'cursor': 'default'}).off('click');
        if (!userRoles.includes('Hotpot Admin')) {
            grid2.wrapper.find('.grid-row').css('pointer-events', 'none');
            grid2.wrapper.find('.btn-open-row').hide();
            setTimeout(disableGear2, 0);
        }
    },
    onload(frm) {        
        updateLocalDescriptions(frm);
    },

    start_time(frm) {
        updateLocalDescriptions(frm);
    },

    end_time(frm) {
        updateLocalDescriptions(frm);
    }
});
function updateLocalDescriptions(frm) {
    if (frm.doc.start_time) {
        const localStartTime = formatUtcToLocal(frm.doc.start_time);
        frm.set_df_property('start_time', 'description', `Local Time: ${localStartTime}`);
    } else {
        frm.set_df_property('start_time', 'description', '');
    }

    if (frm.doc.end_time) {
        const localEndTime = formatUtcToLocal(frm.doc.end_time);
        frm.set_df_property('end_time', 'description', `Local Time: ${localEndTime}`);
    } else {
        frm.set_df_property('end_time', 'description', '');
    }
}

function formatUtcToLocal(utc_datetime) {
    if (!utc_datetime) return "";

    let user_timezone = frappe.sys_defaults.time_zone || Intl.DateTimeFormat().resolvedOptions().timeZone;

    let date = new Date(utc_datetime + "Z");

    let localTime = date.toLocaleTimeString("en-US", {
        timeZone: user_timezone,
        hour: "2-digit",
        minute: "2-digit",
        hour12: true
    });

    return localTime;
}
