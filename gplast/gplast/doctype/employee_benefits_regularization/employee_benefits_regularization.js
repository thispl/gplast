// Copyright (c) 2025, Teampro and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Benefits Regularization', {
	date: function(frm) {
		frm.trigger('calculate_working_hours');
	},
	calculate_working_hours: function(frm){
		if (frm.doc.employee && frm.doc.date) {
			frappe.call({
				method: 'gplast.gplast.doctype.employee_benefits_regularization.employee_benefits_regularization.calculate_ot_hours', 
				args: {
					employee: frm.doc.employee,
					date: frm.doc.date
				},
				callback: function(r) {
					console.log(r.message);
					if (r.message) {
						console.log(r.message);
						frm.set_value('working_hours', r.message);
					}
				}
			});
		}
	}
});
