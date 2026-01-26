// Copyright (c) 2025, Teampro and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Salary Increment Report"] = {

  "filters": [
    {
      "fieldname": "employee",
      "label": "Employee",
      "fieldtype": "Link",
      "options": "Employee"
    },
    {
      "fieldname": "department",
      "label": "Department",
      "fieldtype": "Link",
      "options": "Department"
    },
    {
      "fieldname": "designation",
      "label": "Designation",
      "fieldtype": "Link",
      "options": "Designation"
    }
  ]

};
