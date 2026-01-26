// Copyright (c) 2025, Teampro and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Attendance Report"] = {
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
			"options": "Employee"
		}
	],

	onload: function(report) {
		// wait until report table renders
		setTimeout(() => {
			// select all header cells and center align
			document.querySelectorAll(".dt-header .dt-cell__content").forEach(el => {
				el.style.textAlign = "center";
			});
		}, 500);
	}

	
};
