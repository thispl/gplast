// Copyright (c) 2023, Teampro and contributors
// For license information, please see license.txt

frappe.ui.form.on('Over Time', {


	refresh: function (frm) {
		  if (!frm.doc.__islocal) {
            if (frm.doc.workflow_state === "Preview" && !["Administrator", frm.doc.owner].includes(frappe.session.user)) {
                $.each(frm.fields_dict, function(fieldname, field) {
                    frm.set_df_property(fieldname, "read_only", 1);
                });
                frm.refresh_fields();   
            }
        }
		// frm.page.actions.find(`[data-label='Return']`).remove();
		// frm.page.actions.find(`[data-label='Forward']`).remove();
		// const buttonsToHide = ['Return', 'Forward'];
		// buttonsToHide.forEach(label => {
		// 	const btn = frm.page.actions.find(`[data-label='${label}']`);

		// 	if (btn && btn.length) {
		// 		btn.hide(); 

		// 		let parent = btn.parent();
		// 		if (parent) parent.hide();

		// 		let grandParent = parent.parent();
		// 		if (grandParent) grandParent.hide();
		// 	}
		// });
        // let hod_role = frappe.user_roles.includes("HOD");
        // let supervisor_role = frappe.user_roles.includes("Supervisor")

        //     if (["Pending for Manager", "Pending for Manager 1","Forwarded"].includes(frm.doc.workflow_state)) {
        //         if ((frm.doc.workflow_state == "Pending for Manager" && supervisor_role) || (frm.doc.workflow_state == "Pending for Manager 1" && hod_role) || (frm.doc.workflow_state == "Forwarded" || hod_role)) {
		// 			if (!['Pending for Manager 1', 'Forwarded'].includes(frm.doc.workflow_state)) {
		// 					frm.add_custom_button(__('Forward'), function () {
		// 					let forward_dialog = new frappe.ui.Dialog({
		// 						title: 'Forward Details',
		// 						fields: [
		// 							{
		// 								label: 'Employee ID',
		// 								fieldname: 'employee_id',
		// 								fieldtype: 'Link',
		// 								options: "Employee",
		// 								reqd: 1,
		// 							},
		// 							{
		// 								label: 'Reason',
		// 								fieldname: 'reason',
		// 								fieldtype: 'Small Text',
		// 								reqd: 1
		// 							}
		// 						],
		// 						primary_action_label: 'Forward',
		// 						primary_action(values) {
		// 							forward_dialog.hide();
		// 							frappe.db.get_value('Employee', { name: values.employee_id }, 'user_id')
		// 								.then(response => {
		// 									let user_id = response.message?.user_id;
		// 									if (!user_id) {
		// 										frappe.msgprint(__('The selected Employee ID does not have a User ID.'));
		// 										return;
		// 									}
		// 									frm.set_value("reason", values.reason);
		// 									frm.save().then(() => {
		// 										frappe.call({
		// 											method: "frappe.client.set_value",
		// 											args: {
		// 												doctype: frm.doc.doctype,
		// 												name: frm.doc.name,
		// 												fieldname: "workflow_state",
		// 												value: 'Forwarded',
		// 												ignore_user_permissions: 1,
		// 											},
		// 											callback: function () {
		// 												frappe.call({
		// 													method: 'gplast.custom.resignation_form_mail',
		// 													args: {
		// 														employee_id: values.employee_id,
		// 														reason: values.reason,
		// 														doc_name: frm.doc.name
		// 													},
		// 													callback: function (response) {
		// 														if (response.message) {
		// 															frappe.msgprint(__('Forwarded successfully!'));
		// 															frm.reload_doc();
		// 														}
		// 													}
		// 												});
														
		// 											},
		// 										});
		// 									});
		// 									// frm.save().then(() => {
		// 									//     frm.set_value("workflow_state", "Forwarded");
		// 									//     return frm.save();
		// 									// }).then(() => {
		// 									//     frappe.call({
		// 									//         method: 'gplast.custom.resignation_form_mail',
		// 									//         args: {
		// 									//             employee_id: values.employee_id,
		// 									//             reason: values.reason,
		// 									//             doc_name: frm.doc.name
		// 									//         },
		// 									//         callback: function (response) {
		// 									//             if (response.message) {
		// 									//                 frappe.msgprint(__('Forwarded successfully!'));
		// 									//             }
		// 									//         }
		// 									//     });
		// 									// });
		// 								});
		// 						}
		// 					});
		// 					forward_dialog.show();
		// 				});
		// 			}

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
        //                 else if (frm.doc.workflow_state === "Pending for Manager 1") {
        //                     previous_state = "Returned";
        //                 } 
        //                 else if (frm.doc.workflow_state === "Pending for Manager") {
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
	employee(frm){
		frappe.call({
			'method':'frappe.client.get_value',
			'args':{
				'doctype':'Employee',
				'filters':{
					'name':frm.doc.employee,
				},
				'fieldname':['ot_eligibility']
			},
			callback(r){
				if(r.message){
					
					if(r.message.ot_eligibility != 'Over Time'){
						frappe.msgprint("This Employee not Applicable for OT")
						
					}
					
					
				}
			
			}
		})
	},
	ot_date: function(frm) {
		frm.trigger('get_total_ot_hours');
	},
	validate(frm){
		frm.trigger('validate_overtime_hours');
		frappe.call({
			'method':'frappe.client.get_value',
			'args':{
				'doctype':'Employee',
				'filters':{
					'name':frm.doc.employee,
				},
				'fieldname':['ot_eligibility']
			},
			callback(r){
				if(r.message){
					
					if(r.message.ot_eligibility != 'Over Time'){
						frappe.msgprint("This Employee not Applicable for OT")
						frappe.validated = false
					}
					
					
				}
			
			}
		})
	},
	validate_overtime_hours(frm){
		if (frm.doc.employee && frm.doc.ot_date) {
            frappe.call({
                "method": "gplast.gplast.doctype.over_time.over_time.get_total_ot_hours",
                "args": {
                    "employee": frm.doc.employee,
                    "ot_date": frm.doc.ot_date,
                },
                callback(r) {
                    $.each(r.message, function (i, v) {
                        console.log(r.message)
						if (v.overtime_hours < frm.doc.overtime_hours){
							frappe.validated = false
							frappe.msgprint('Not Allowed to update the OT hours more than the Actual OT Hours')
							frappe.validated = false
						}
                    });
                }
            });
        
        }
		
	},
	get_total_ot_hours: function (frm) {
        if (frm.doc.employee && frm.doc.ot_date) {
			console.log('message')
            frappe.call({
                "method": "gplast.gplast.doctype.over_time.over_time.get_total_ot_hours",
                "args": {
                    "employee": frm.doc.employee,
                    "ot_date": frm.doc.ot_date,
                },
                callback(r) {
                    $.each(r.message, function (i, v) {
                        console.log(r.message)
						frm.set_value('ot_hour', v.ot_hours);
						frm.set_value('overtime_hours', v.overtime_hours);
						frm.set_value('shift', v.shift);
                    });
                }
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
