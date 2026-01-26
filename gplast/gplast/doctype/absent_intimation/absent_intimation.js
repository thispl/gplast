// Copyright (c) 2025, Teampro and contributors
// For license information, please see license.txt

frappe.ui.form.on('Absent Intimation', {
	from_date(frm) {
        validate_dates(frm);
    },
    to_date(frm) {
        validate_dates(frm);
    }
});
function validate_dates(frm) {
    if (frm.doc.from_date && frm.doc.to_date && frm.doc.from_date > frm.doc.to_date) {
        // frm.set_value('last_leave_availed_from_date', '');
        frm.set_value('from_date', '');
        frm.set_value('to_date', '');
        frappe.throw(__('From Date cannot be after To Date'));
    }
}
