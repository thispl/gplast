// Copyright (c) 2025, Teampro and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Report Late Entry"] = {
	"filters": [
		{
			"label": __("From Date"),
			"fieldname": "from_date",
			"fieldtype": "Date",
			"reqd": 1
		},
		{
			"label": __("To Date"),
			"fieldname": "to_date",
			"fieldtype": "Date",
			"reqd": 1
		},
		{
			"label": __("Employee"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",

			"get_query": function () {

				if (frappe.user_roles.includes("HR User")) {
					return {
						query: "gplast.gplast.report.attendance_summary_report.attendance_summary_report.get_all_active_employees"
					};
				}


				else if (frappe.user_roles.includes("HOD")) {
					return {
						query: "gplast.gplast.report.attendance_summary_report.attendance_summary_report.get_employees_by_user_department"
					};
				}

				return {
					filters: {
						status: "Active",
						user_id: frappe.session.user
					}
				};
			},

		}


	]
};
