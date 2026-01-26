// Copyright (c) 2025, Teampro and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Leave Balance Report"] = {
	"filters": [
		{
			fieldname: "employee",
			label: __("Employee"),
			fieldtype: "Link",
			options: "Employee",
			default: frappe.session.user === "Administrator" ? "" : frappe.user_info().employee,
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_start()
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_end()
		}
	],

onload: function(report) {
		if (frappe.session.user !== "Administrator") {
			frappe.db.get_value("Employee", { user_id: frappe.session.user }, "name")
				.then(r => {
					if (r && r.message) {
						report.set_filter_value("employee", r.message.name);
					}
				});
		}
	}
};
