// Copyright (c) 2025, Teampro and contributors
// For license information, please see license.txt

frappe.ui.form.on('Report Staffing Plan', {
	// refresh: function(frm) {

	// }
	onload: function(frm){
		frm.disable_save();
		// frappe.call({
        //     method: "gplast.gplast.doctype.report_staffing_plan.report_staffing_plan.get_department",
        //     args:{
        //         user:user,
        //     },
        //     callback(r) {
        //         // if (frappe.session.user === "Administrator" || !emp) {
        //         //     frm.set_query('cost_center', () => {
        //         //         return {
        //         //             filters: {
        //         //                 workflow_state: 'Approved'
        //         //             }
        //         //         }
        //         //     });
        //         //     return; 
        //         // }

        //         if (r.message) {
		// 			console.log(r.message);

		// 			var cost_center = r.message.cost_center;    
		// 			var department_list = r.message.departments;
						
		// 			frm.set_df_property('cost_center', 'read_only', 1);

		// 			frm.set_query('cost_center', () => {
		// 				return {
		// 					filters: {
		// 						cost_center: cost_center,
		// 						workflow_state: 'Approved'
		// 					}
		// 				}
		// 			});

		// 			frm.set_query('department', () => {
		// 				console.log(department_list);
		// 				return {
		// 					filters: {
		// 						name: ["in", department_list],
		// 						workflow_state: 'Approved'
		// 					}
		// 				}
		// 			});
		// 		}
		// 	}
			
		// });		
		frappe.call({
			method: "gplast.gplast.doctype.report_staffing_plan.report_staffing_plan.get_department",
			args: {
				user: user,
			},
			callback(r) {
				frappe.call({
					method: "frappe.client.get_value",
					args: {
						doctype: "Employee",
						filters: { user_id: frappe.session.user },
						fieldname: "name"
					},
					callback: function(res) {
						var emp = res.message ? res.message.name : null;
						if (frappe.session.user === "Administrator" || !emp) {
							frm.set_df_property('cost_center', 'read_only', 0);
							frm.set_query('cost_center', () => {
								return {
									filters: {
										workflow_state: 'Approved'
									}
								}
							});

							return; 
						}
						if (r.message) {

							console.log(r.message);

							var cost_center = r.message.cost_center;    
							var department_list = r.message.departments;

							frm.set_df_property('cost_center', 'read_only', 1);

							frm.set_query('cost_center', () => {
								return {
									filters: {
										cost_center: cost_center,
										workflow_state: 'Approved'
									}
								}
							});

							frm.set_query('department', () => {
								console.log(department_list);
								return {
									filters: {
										name: ["in", department_list],
										workflow_state: 'Approved'
									}
								}
							});
						}
					}
				});
			}
		});
	
		frappe.call({
			method:"gplast.gplast.doctype.report_staffing_plan.report_staffing_plan.report_staffing_plan",
			args: {
				"cost__center": frm.doc.cost_center,
				"department": frm.doc.department
			},
			freeze: true,
			freeze_message: "Getting Data.....",
			callback: function(r) {
                frm.fields_dict.staffing_plan.$wrapper.empty().append(r.message);
            }
		})
	},
	cost_center: function(frm){
		frappe.call({
			method:"gplast.gplast.doctype.report_staffing_plan.report_staffing_plan.report_staffing_plan",
			args: {
				"cost__center": frm.doc.cost_center,
				"department": frm.doc.department
			},
			freeze: true,
			freeze_message: "Getting Data.....",
			callback: function(r) {
				frm.fields_dict.staffing_plan.$wrapper.empty().append(r.message);
			}
		})
	},
	department: function(frm){
		
		frappe.call({
				method:"gplast.gplast.doctype.report_staffing_plan.report_staffing_plan.report_staffing_plan",
				args: {
					"cost__center": frm.doc.cost_center,
					"department": frm.doc.department
				},
				freeze: true,
				freeze_message: "Getting Data.....",
				callback: function(r) {
					frm.fields_dict.staffing_plan.$wrapper.empty().append(r.message);
				}
			})
			frappe.call({
				method: "gplast.gplast.doctype.report_staffing_plan.report_staffing_plan.get_department",
				args:{
					user:user,
				},
				callback(r) {
					if (frappe.session.user === "Administrator") {
						frm.set_query('cost_center', () => {
							return {
								filters: {
									workflow_state: 'Approved'
								}
							}
						});
						return; 
					}
					if (r.message) {
						console.log(r.message);

						// var cost_center = r.message.cost_center;    
						var department_list = r.message.departments;
							
						frm.set_df_property('cost_center', 'read_only', 1);
						frm.set_query('department', () => {
							console.log(department_list);
							return {
								filters: {
									name: ["in", department_list],
									workflow_state: 'Approved'
								}
							}
						});
					}
				}
			});
			
		},
	// after_save: function(frm) {
	// 	frm.reload_doc();
	// }
});