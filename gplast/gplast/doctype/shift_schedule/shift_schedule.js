// Copyright (c) 2023, Teampro and contributors
// For license information, please see license.txt

frappe.ui.form.on('Shift Schedule', {
	get_template: function (frm) {
        window.location.href = repl(frappe.request.url +
            '?cmd=%(cmd)s&from_date=%(from_date)s&to_date=%(to_date)s&department=%(department)s', {
            cmd: "gplast.gplast.doctype.shift_schedule.shift_schedule.get_template",
            from_date: frm.doc.from_date,
            to_date: frm.doc.to_date,
            department:frm.doc.department,
        })
	},	

    refresh: function(frm) {
		  if (!frm.doc.__islocal) {
            if (frm.doc.workflow_state === "Preview" && !["Administrator", frm.doc.owner].includes(frappe.session.user)) {
                $.each(frm.fields_dict, function(fieldname, field) {
                    frm.set_df_property(fieldname, "read_only", 1);
                });
                frm.refresh_fields();   
            }
        }
	}
});
