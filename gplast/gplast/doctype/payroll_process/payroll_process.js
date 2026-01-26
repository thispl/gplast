// Copyright (c) 2023, Teampro and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payroll Process', {
	process_late(frm){
		frappe.call({
			"method": "gplast.utility.attendance_calc",
			"args":{
				"from_date" : frm.doc.start_date,
				"to_date" : frm.doc.end_date,
			},
			freeze: true,
			freeze_message: 'Processing late....',
			callback(r){
				console.log(r.message)
				if(r.message == "ok"){
					frappe.msgprint("Late Penalty Created Successfully")
				}
			}
		})
	},
	create_late_penalty(frm){
		frappe.call({
			"method": "gplast.utility.additional_salary",
			"args":{
				"from_date" : frm.doc.start_date,
				"to_date" : frm.doc.end_date,
			},
			freeze: true,
			freeze_message: 'Processing additional salary....',
			callback(r){
				console.log(r.message)
				if(r.message == "ok"){
					frappe.msgprint("Late Penalty - Additional Created Successfully")
				}
			}
		})
	},
	process_permission(frm){
		frappe.call({
			"method": "gplast.utility.process_permission",
			"args":{
				"from_date" : frm.doc.start_date,
				"to_date" : frm.doc.end_date,
			},
			freeze: true,
			freeze_message: 'Processing Attendance Permission....',
			callback(r){
				console.log(r.message)
				if(r.message == "ok"){
					frappe.msgprint("Leave Permission Created Successfully")
				}
			}
		})
	},
	create_leave_ledger_entry(frm){
		frappe.call({
			"method": "gplast.utility.leave_permission",
			"args":{
				"from_date" : frm.doc.start_date,
				"to_date" : frm.doc.end_date,
				'leave_deduction':frm.doc.leave_deduction,
				
			},
			freeze: true,
			freeze_message: 'Processing Leave Deduction....',
			callback(r){
				console.log(r.message)
				if(r.message == "ok"){
					frappe.msgprint(" Leave Ledger Entry Created Successfully")
				}
			}
		})
	}
});
