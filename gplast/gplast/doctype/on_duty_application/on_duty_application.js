// Copyright (c) 2023, Teampro and contributors
// For license information, please see license.txt

frappe.ui.form.on('On Duty Application', {

	refresh: function(frm) {
		  if (!frm.doc.__islocal) {
            if (frm.doc.workflow_state === "Preview" && !["Administrator", frm.doc.owner].includes(frappe.session.user)) {
                $.each(frm.fields_dict, function(fieldname, field) {
                    frm.set_df_property(fieldname, "read_only", 1);
                });
                frm.refresh_fields();   
            }
        }
        

	},
    
    employee(frm){
        if (frm.doc.shift_group) {
            frm.set_query("shift", function () {
                return {
                    filters: {
                        shift_group: frm.doc.shift_group
                    }
                };
            });
        }
    },
    before_save: function(frm) {
            frappe.db.get_value('Approvers', { 'employee': frm.doc.employee }, 'total_number_of_approvers')
                .then(response => {
                    if (response.message) {
                        frm.set_value('total_leave_approvers', response.message.total_number_of_approvers);
                        frm.refresh_field('total_leave_approvers');
                    }
                });
    }


    


});
