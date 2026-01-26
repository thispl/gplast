// Copyright (c) 2025, Teampro and contributors
// For license information, please see license.txt

frappe.ui.form.on('Leave Revocation', {
	from_date(frm) {
		// frm.trigger(validate_date_range);
		if(frm.doc.from_date && frm.doc.to_date){   
			if(frm.doc.from_date > frm.doc.to_date){
				frm.set_value('from_date','')
				frappe.throw("To date must be greater than from date")
			}      
            var start = frappe.datetime.obj_to_str(frm.doc.from_date);
            var end = frappe.datetime.obj_to_str(frm.doc.to_date);
            var difference = frappe.datetime.get_day_diff(end,start);
            if(difference >=0){
                frm.set_value("total_leave_in_days",difference + 1);
            }
            else{
                frm.set_value("total_leave_in_days",0);
            }
        }
	},
	to_date(frm){
		// frm.trigger(validate_date_range);
	   if(frm.doc.from_date && frm.doc.to_date){   
			if(frm.doc.from_date > frm.doc.to_date){
				frm.set_value('to_date','')
				frappe.throw("To date must be greater than from date")
			}   
            var start = frappe.datetime.obj_to_str(frm.doc.from_date);
            var end = frappe.datetime.obj_to_str(frm.doc.to_date);
            var difference = frappe.datetime.get_day_diff(end,start);
            if(difference >=0){
                frm.set_value("total_leave_in_days",difference + 1);
            }
            else{
                frm.set_value("total_leave_in_days",0);
            }
        } 
	},
	validate_date_range(frm) {
		const from = frm.doc.from_date;
		const to = frm.doc.to_date;
	
		if (from && to) {
			if (frappe.datetime.get_diff(to, from) < 0) {
				if (changed_field === "to_date") {
					frm.set_value("to_date", null);
					frappe.msgprint(__("To Date must be greater than or equal to From Date."));
				} else if (changed_field === "from_date") {
					frm.set_value("from_date", null);
					frappe.msgprint(__("From Date must be less than or equal to To Date."));
				}
			}
		}
	}
});
