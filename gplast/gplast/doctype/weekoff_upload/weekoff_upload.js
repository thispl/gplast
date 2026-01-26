// Copyright (c) 2025, Teampro and contributors
// For license information, please see license.txt

frappe.ui.form.on('Weekoff upload', {
	get_template: function (frm) {
			window.location.href = repl(frappe.request.url +
				'?cmd=%(cmd)s&from_date=%(from_date)s&to_date=%(to_date)s&department=%(department)s&employee_type=%(employee_type)s&name=%(name)s&employment_type=%(employment_type)s',{
				cmd: "gplast.gplast.doctype.weekoff_upload.weekoff_upload.get_template",
				from_date: frm.doc.from_date,
				to_date: frm.doc.to_date,
				department:frm.doc.department,
				designation:frm.doc.employee_type,
				employment_type:frm.doc.employment_type,
				name:frm.doc.name
			})
		},

		from_date(frm) {
			if(frm.doc.from_date && frm.doc.to_date){   
				if(frm.doc.from_date > frm.doc.to_date){
					frm.set_value('from_date','')
					frappe.throw("To date must be greater than from date")
				}      
			}
		},
		to_date(frm){
		   if(frm.doc.from_date && frm.doc.to_date){   
				if(frm.doc.from_date > frm.doc.to_date){
					frm.set_value('to_date','')
					frappe.throw("To date must be greater than from date")
				}   
		}
	}
});
