// Copyright (c) 2025, Teampro and contributors
// For license information, please see license.txt

frappe.ui.form.on('Resignation Form', {


    refresh: function (frm) {
          if (!frm.doc.__islocal) {
            if (frm.doc.workflow_state === "Preview" && !["Administrator", frm.doc.owner].includes(frappe.session.user)) {
                $.each(frm.fields_dict, function(fieldname, field) {
                    frm.set_df_property(fieldname, "read_only", 1);
                });
                frm.refresh_fields();   
            }
        }
        
        // const buttonsToHide = ['Return', 'Forward'];
        
        //     buttonsToHide.forEach(label => {
        //         const btn = frm.page.actions.find(`[data-label='${label}']`);
        
        //         if (btn && btn.length) {
        //             btn.hide(); // hide the button itself
        
        //             let parent = btn.parent();
        //             if (parent) parent.hide();
        
        //             let grandParent = parent.parent();
        //             if (grandParent) grandParent.hide();
        //         }
        //     });
        // // let employee_role = frappe.user_roles.includes("Employee");
        // let hod_role = frappe.user_roles.includes("HOD");
        // let hr_role = ["HR User", "HR Manager"].some(role=> frappe.user_roles.includes(role));
        // let coo_role = frappe.user_roles.includes("COO")

        //     if (["Pending for HOD", "Pending for HR", "Pending for COO","Forwarded"].includes(frm.doc.workflow_state)) {
        //         if (frm.doc.workflow_state == "Pending for HOD" && hod_role || frm.doc.workflow_state == "Pending for HR" && hr_role || frm.doc.workflow_state == "Pending for COO" && coo_role) {
        //         if (frm.doc.workflow_state !='Pending for COO'){
        //             frm.add_custom_button(__('Forward'), function () {
        //             let forward_dialog = new frappe.ui.Dialog({
        //                 title: 'Forward Details',
        //                 fields: [
        //                     {
        //                         label: 'Employee ID',
        //                         fieldname: 'employee_id',
        //                         fieldtype: 'Link',
        //                         options: "Employee",
        //                         reqd: 1,
        //                     },
        //                     {
        //                         label: 'Reason',
        //                         fieldname: 'reason',
        //                         fieldtype: 'Small Text',
        //                         reqd: 1
        //                     }
        //                 ],
        //                 primary_action_label: 'Forward',
        //                 primary_action(values) {
        //                     forward_dialog.hide();
        //                     frappe.db.get_value('Employee', { name: values.employee_id }, 'user_id')
        //                         .then(response => {
        //                             let user_id = response.message?.user_id;
        //                             if (!user_id) {
        //                                 frappe.msgprint(__('The selected Employee ID does not have a User ID.'));
        //                                 return;
        //                             }
        //                             frm.set_value("test", user_id);
        //                             frm.set_value("reason", values.reason);
        //                             frm.save().then(() => {
        //                                 frappe.call({
        //                                     method: "frappe.client.set_value",
        //                                     args: {
        //                                         doctype: frm.doc.doctype,
        //                                         name: frm.doc.name,
        //                                         fieldname: "workflow_state",
        //                                         value: 'Forwarded',
        //                                         ignore_user_permissions: 1,
        //                                     },
        //                                     callback: function () {
        //                                         frappe.call({
        //                                             method: 'gplast.custom.resignation_form_mail',
        //                                             args: {
        //                                                 employee_id: values.employee_id,
        //                                                 reason: values.reason,
        //                                                 doc_name: frm.doc.name
        //                                             },
        //                                             callback: function (response) {
        //                                                 if (response.message) {
        //                                                     frappe.msgprint(__('Forwarded successfully!'));
        //                                                     frm.reload_doc();
        //                                                 }
        //                                             }
        //                                         });
                                                
        //                                     },
        //                                 });
        //                             });
        //                             // frm.save().then(() => {
        //                             //     frm.set_value("workflow_state", "Forwarded");
        //                             //     return frm.save();
        //                             // }).then(() => {
        //                             //     frappe.call({
        //                             //         method: 'gplast.custom.resignation_form_mail',
        //                             //         args: {
        //                             //             employee_id: values.employee_id,
        //                             //             reason: values.reason,
        //                             //             doc_name: frm.doc.name
        //                             //         },
        //                             //         callback: function (response) {
        //                             //             if (response.message) {
        //                             //                 frappe.msgprint(__('Forwarded successfully!'));
        //                             //             }
        //                             //         }
        //                             //     });
        //                             // });
        //                         });
        //                 }
        //             });
        //             forward_dialog.show();
        //         });
        //     }

        //         frm.add_custom_button(__('Return'), function () {
        //         let dialog = new frappe.ui.Dialog({
        //             title: "Reason for Return",
        //             fields: [
        //                 {
        //                     label: "Reason",
        //                     fieldname: "reason",
        //                     fieldtype: "Small Text",
        //                     reqd: 1,
        //                 },
        //             ],
        //             primary_action_label: "Return",
        //             primary_action(values) {
        //                 dialog.hide();
        //                 let previous_state = "";
        //                 if (frm.doc.workflow_state === "Pending for COO") {
        //                     previous_state = "Returned";
        //                 } 
        //                 else if (frm.doc.workflow_state === "Pending for HR") {
        //                     previous_state = "Returned";
        //                 } 
        //                 else if (frm.doc.workflow_state === "Pending for HOD") {
        //                     previous_state = "Returned";
        //                 } 
        //                 else if (frm.doc.workflow_state === "Forwarded") {
        //                     previous_state = "Returned";
        //                 }
        //                 else {
        //                     frappe.msgprint(__('Invalid workflow state for return.'));
        //                     return;
        //                 }
        //                 frm.set_value("reason", values.reason);
        //                 // frm.set_value("re", values.reason);
        //                 // frm.set_value("sa", 1);
        //                 frm.save().then(() => {
        //                     frappe.call({
        //                         method: "frappe.client.set_value",
        //                         args: {
        //                             doctype: frm.doc.doctype,
        //                             name: frm.doc.name,
        //                             fieldname: "workflow_state",
        //                             value: previous_state,
        //                             ignore_user_permissions: 1,
        //                         },
        //                         callback: function () {
        //                             frappe.msgprint(__('Returned Successfully.'));
        //                             frm.reload_doc();
        //                         },
        //                     });
        //                 });
        //             },
        //         });

        //         dialog.show();
        //     });
        //     }
        // }
    },

    test: function (frm) {
        if (frm.doc.workflow_state === "Forwarded") {
            frm.set_value("test", "");
        }
    },

    onload: function(frm){
        if (frm.doc.owner != frappe.session.user && frm.doc.workflow_state =='Preview'){
            frm.set_df_property('reason','read_only',1);
            frm.set_df_property('hods_relieving_date','read_only',1);
            frm.set_df_property('attach','read_only',1);
        }
        else{
            frm.set_df_property('reason','read_only',0);
            frm.set_df_property('hods_relieving_date','read_only',0);
            frm.set_df_property('attach','read_only',0);
        }
    },
    before_save: function(frm) {
            frappe.db.get_value('Approvers', { 'employee': frm.doc.employee }, 'total_number_of_approvers')
                .then(response => {
                    if (response.message) {
                        frm.set_value('total_approver_', response.message.total_number_of_approvers);
                        frm.refresh_field('total_approver_');
                    }
                });
    }
});
