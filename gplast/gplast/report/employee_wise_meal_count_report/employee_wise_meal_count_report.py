# Copyright (c) 2023, Teampro and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = [
        _("Date") + ":Date:140",
        _("Employee") + ":Link/Employee:140",
        _("Employee Name") + ":Data:140",
        _("Branch") + ":Data:140",
        _("Breakfast") + ":Int:80",
        _("Lunch") + ":Int:80",
        _("Dinner") + ":Int:80",
        _("Total Count") + ":Int:80"
    ]

    # Construct the filters for the query
    query_filters = {}

    # Add date range filter to the query filters
    if filters.get("from_date") and filters.get("to_date"):
        query_filters["date"] = ["between", [filters.get("from_date"), filters.get("to_date")]]

    # Add employee filter to the query filters if provided
    if filters.get("employee"):
        query_filters["employee"] = filters.get("employee")

    # Check if branch filter is provided, add it to the query filters
    if filters.get("branch"):
        query_filters["branch"] = filters.get("branch")

    # Fetch data from Food Count DocType with correct date, employee, and branch filter
    data = frappe.get_all("Food Count", filters=query_filters, fields=["date", "employee", "meal_type", "employee_name", "branch"])

    # Dictionary to store counts for each unique combination of date, employee, employee_name, and branch
    count_dict = {}

    for row in data:
        # Create a unique key for the combination of date, employee, employee_name, and branch
        key = (row["date"], row["employee"], row["employee_name"], row["branch"])

        # Initialize counts if the key is not in the dictionary
        if key not in count_dict:
            count_dict[key] = {
                "Breakfast": 0,
                "Lunch": 0,
                "Dinner": 0
            }

        # Update counts based on meal type
        meal_type = row["meal_type"]
        if meal_type == "Breakfast":
            count_dict[key]["Breakfast"] += 1
        elif meal_type == "Lunch":
            count_dict[key]["Lunch"] += 1
        elif meal_type == "Dinner":
            count_dict[key]["Dinner"] += 1

    result = []

    for key, counts in count_dict.items():
        # Append data to the result
        result.append([key[0], key[1], key[2], key[3], counts["Breakfast"], counts["Lunch"], counts["Dinner"], counts["Breakfast"] + counts["Lunch"] + counts["Dinner"]])

    return columns, result