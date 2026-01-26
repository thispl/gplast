// Copyright (c) 2025, Teampro and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payroll - Early Exit Penalty Processing', {
	process_early_exit(frm){
		frappe.call({
			"method": "gplast.utility.early_exit_calc",
			"args":{
				"from_date" : frm.doc.start_date,
				"to_date" : frm.doc.end_date,
			},
			freeze: true,
			freeze_message: 'Processing late....',
			callback(r){
				console.log(r.message)
				if(r.message){
					frappe.msgprint("Early Exit Created Successfully")
				}
			}
		})
	},
	create_early_exit_penalty(frm){
		frappe.call({
			"method": "gplast.utility.early_exit_additional_salary",
			"args":{
				"from_date" : frm.doc.start_date,
				"to_date" : frm.doc.end_date,
			},
			freeze: true,
			freeze_message: 'Processing additional salary....',
			callback(r){
				console.log(r.message)
				if(r.message == "ok"){
					frappe.msgprint("Early Exit - Additional Created Successfully")
				}
			}
		})
	}
});
