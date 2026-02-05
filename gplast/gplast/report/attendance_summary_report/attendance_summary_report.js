// Copyright (c) 2025, Teampro and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Attendance Summary Report"] = {
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

		// {
		// 	"label": __("Employee"),
		// 	"fieldname": "employee",
		// 	"fieldtype": "Link",
		// 	"options": "Employee",
		// 	"on_change": function() {
		// 		let employee = frappe.query_report.get_filter_value("employee");

		// 		if (employee) {
		// 			frappe.db.get_value(
		// 				"Employee",
		// 				employee,
		// 				["employee_name", "designation_code", "designation", "department"]
		// 			).then(r => {
		// 				if (r.message) {
		// 					frappe.query_report.set_filter_value("employee_name", r.message.employee_name);
		// 					frappe.query_report.set_filter_value("designation_code", r.message.designation_code);
		// 					frappe.query_report.set_filter_value("designation", r.message.designation);
		// 					frappe.query_report.set_filter_value("department", r.message.department);
		// 				}
		// 			});
		// 		} else {
		// 			frappe.query_report.set_filter_value("employee_name", "");
		// 			frappe.query_report.set_filter_value("designation_code", "");
		// 			frappe.query_report.set_filter_value("designation", "");
		// 			frappe.query_report.set_filter_value("department", "");
		// 		}
		// 	}
		// },

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

			"on_change": function() {
				let employee = frappe.query_report.get_filter_value("employee");

				if (employee) {
					frappe.db.get_value(
						"Employee",
						employee,
						["employee_name", "designation_code", "designation", "department"]
					).then(r => {
						if (r.message) {
							frappe.query_report.set_filter_value("employee_name", r.message.employee_name);
							frappe.query_report.set_filter_value("designation_code", r.message.designation_code);
							frappe.query_report.set_filter_value("designation", r.message.designation);
							frappe.query_report.set_filter_value("department", r.message.department);
						}
					});
				} else {
					frappe.query_report.set_filter_value("employee_name", "");
					frappe.query_report.set_filter_value("designation_code", "");
					frappe.query_report.set_filter_value("designation", "");
					frappe.query_report.set_filter_value("department", "");
				}
			}
		},


		{
			"label": __("Employee Name"),
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"read_only": 1
		},
		{
			"label": __("Designaiton Code"),
			"fieldname": "designation_code",
			"fieldtype": "Data",
			"read_only": 1
		},
		{
			"label": __("Designation"),
			"fieldname": "designation",
			"fieldtype": "Data",
			"read_only": 1
		},
		{
			"label": __("Department"),
			"fieldname": "department",
			"fieldtype": "Data",
			"read_only": 1
		}
	]
};
