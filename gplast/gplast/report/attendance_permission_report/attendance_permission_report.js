// Copyright (c) 2025, Teampro and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Attendance Permission Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
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
