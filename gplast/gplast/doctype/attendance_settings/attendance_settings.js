// Copyright (c) 2025, Teampro and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance Settings', {
	refresh: function(frm) {
		frm.disable_save();
	},
	onload: function(frm) {
		frm.disable_save()
	},
	process_checkin(frm){
		if (frm.doc.from_date && frm.doc.to_date){
			if (frm.doc.employee) {
				frm.set_value("employee", "")
			}
			frappe.call({
				"method": "gplast.mark_checkin.mark_employee_checkin_fontend_enqueue",
				"args":{
					"from_date" : frm.doc.from_date,
					"to_date": frm.doc.to_date
				},
				freeze: true,
				freeze_message: 'Processing Checkin....',
				callback(r){
					if(r.message == "ok"){
						frappe.msgprint("Checkins are running in background.")
					}
				}
			})
		}
	},
	process_att(frm){
		if (frm.doc.employee && frm.doc.from_date && frm.doc.to_date){
			frappe.call({
				"method": "gplast.mark_attendance.mark_att_with_employee",
				"args":{
					"from_date" : frm.doc.from_date,
					"to_date": frm.doc.to_date,
					"employee": frm.doc.employee 
				},
				freeze: true,
				freeze_message: 'Processing Attendance....',
				callback(r){
					if(r.message == "ok"){
						frappe.msgprint("The Attendance has been Updated")
					}
				}
			})
		}
		else{
			frappe.call({
				"method": "gplast.mark_attendance.mark_att_frontend_enqueue",
				"args":{
					"from_date" : frm.doc.from_date,
					"to_date": frm.doc.to_date 
				},
				freeze: true,
				freeze_message: 'Processing Attendance....',
				callback(r){
					if(r.message == "ok"){
						frappe.msgprint("Attendance are running in background.")
					}
				}
			})
		}
	},
	submit_week_off_attendance(frm){
		if (frm.doc.employee && frm.doc.from_date && frm.doc.to_date){
			frappe.call({
				"method": "gplast.mark_attendance.mark_att_with_employee_ww_submit",
				"args":{
					"from_date" : frm.doc.from_date,
					"to_date": frm.doc.to_date,
					"employee": frm.doc.employee 
				},
				freeze: true,
				freeze_message: 'Submitting Attendance....',
				callback(r){
					if(r.message == "ok"){
						frappe.msgprint("The Attendance has been Submitted")
					}
				}
			})
		}
		else{
			frappe.call({
				"method": "gplast.mark_attendance.mark_att_for_all_ww_submit",
				"args":{
					"from_date" : frm.doc.from_date,
					"to_date": frm.doc.to_date 
				},
				freeze: true,
				freeze_message: 'Submitting Attendance....',
				callback(r){
					if(r.message == "ok"){
						frappe.msgprint("The Attendance has been Submitted")
					}
				}
			})
		}
	},	
	process_ur(frm) {
		if (frm.doc.employee && frm.doc.from_date && frm.doc.to_date){
			frappe.call({
				"method": "gplast.mark_checkin.mark_unregistered_emp_enqueue",
				"args":{
					"from_date" : frm.doc.from_date,
					"to_date": frm.doc.to_date,
					"employee": frm.doc.employee 
				},
				freeze: true,
				freeze_message: 'Processing Unregistered Checkins....',
				callback(r){
					if(r.message == "ok"){
						frappe.msgprint("Unregistered Checkins are running in background.")
					}
				}
			})
		}
		else {
			frappe.call({
				"method": "gplast.mark_checkin.mark_unregistered_enqueue",
				"args":{
					"from_date" : frm.doc.from_date,
					"to_date": frm.doc.to_date 
				},
				freeze: true,
				freeze_message: 'Processing Unregistered Checkins....',
				callback(r){
					if(r.message == "ok"){
						frappe.msgprint("Unregistered Checkins are running in background.")
					}
				}
			})
		}
	}
});
