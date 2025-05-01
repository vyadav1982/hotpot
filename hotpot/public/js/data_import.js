
frappe.ui.form.on('Data Import', {
    refresh: function(frm) {
        const roles = frappe.user_roles;
        const isAdmin = roles.includes("Administrator");
        if(!isAdmin){
        frm.page.remove_inner_button(__("Don't Send Emails"));
        frm.page.wrapper.find(".comment-box").css({'display':'none'});
        
        if(!frm.doc.reference_doctype) {
            if(roles.includes("Hotpot Vendor")){
                frm.set_query('reference_doctype', function() {
                    return {
                        filters: {
                            name: ['in', ['Hotpot Meal']]
                        }
                    };});
            }
            else{
            frm.set_query('reference_doctype', function() {
                return {
                    filters: {
                        name: ['in', ['Hotpot User', 'Hotpot Meal']]
                    }
                };
            });
        }
        }
        
        if(frm.doc.reference_doctype) {
            frm.page.clear_menu()
            frm.page.hide_menu()
            frm.page.add_inner_button(__("Download Template", null, "Button in list view menu"), function () {
                frappe.call({
                            method: "hotpot.utils.get_filtered_import_template.get_filtered_import_template",
                            args: {
                                doctype: frm.doc.reference_doctype
                            },
                            callback: function(r) {
                                if (r.message && r.message.file_content && r.message.filename) {
                                    const byteCharacters = atob(r.message.file_content);
                                    const byteNumbers = new Array(byteCharacters.length);
                                    for (let i = 0; i < byteCharacters.length; i++) {
                                        byteNumbers[i] = byteCharacters.charCodeAt(i);
                                    }
                                    const byteArray = new Uint8Array(byteNumbers);
                                    const blob = new Blob([byteArray], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
                                
                                    const link = document.createElement('a');
                                    link.href = window.URL.createObjectURL(blob);
                                    link.download = r.message.filename;
                                    document.body.appendChild(link);
                                    link.click();
                                    document.body.removeChild(link);
                                }
                            }
                        });
            });
            
        }
        frm.set_df_property("mute_emails","hidden",1);
        frm.set_df_property("google_sheets_url","hidden",1);
        frm.set_df_property("download_template","hidden",1)
        frm.set_df_property("html_5","hidden",1)
        frm.set_df_property("import_type","options","Insert New Records");
    }
    },
});


// cur_frm.page.clear_menu()
// mute_emails
// google_sheets_url