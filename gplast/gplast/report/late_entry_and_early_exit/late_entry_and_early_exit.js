// Copyright (c) 2025, Teampro and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Late Entry And Early Exit"] = {
	"filters": [

		{
			"label":__("From Date"),
			"fieldname":"from_date",
			"fieldtype":"Date",
			"reqd":1
		},
		{
			"label":__("To Date"),
			"fieldname":"to_date",
			"fieldtype":"Date",
			"reqd":1
		},
		{
			"label":__("Employee"),
			"fieldname":"employee",
			"fieldtype":"Link",
			"options":"Employee"
		}

	]
};
