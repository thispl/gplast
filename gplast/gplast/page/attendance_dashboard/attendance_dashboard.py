import frappe
from frappe.utils import get_datetime

@frappe.whitelist()
def get_shift_wise_attendance(from_date, to_date, status=None, shift=None):

    conditions = []
    values = {
        "from_date": from_date,
        "to_date": to_date
    }

    allowed_departments = get_allowed_departments()

    if allowed_departments is not None:
        if not allowed_departments:
            return []
        conditions.append("att.department IN %(departments)s")
        values["departments"] = tuple(allowed_departments)

    if status:
        conditions.append("att.status = %(status)s")
        values["status"] = status

    if shift:
        conditions.append("att.shift = %(shift)s")
        values["shift"] = shift

    condition_str = " AND ".join(conditions)
    if condition_str:
        condition_str = " AND " + condition_str

    return frappe.db.sql(f"""
        SELECT
            att.employee,
            att.employee_name,
            emp.employee_category,
            att.department,
            att.unit,
            att.shift,
            att.in_time,
            att.out_time,
            att.total_working_hours,
            IFNULL(att.overtime_hours, 0) AS ot_hours
        FROM `tabAttendance` att
        LEFT JOIN `tabEmployee` emp
            ON emp.name = att.employee
        WHERE att.attendance_date BETWEEN %(from_date)s AND %(to_date)s
        {condition_str}
        ORDER BY att.employee_name
    """, values, as_dict=1)

@frappe.whitelist()
def get_shift_count(from_date, to_date, status=None):

    conditions = []
    values = {
        "from_date": from_date,
        "to_date": to_date
    }

    allowed_departments = get_allowed_departments()

    if allowed_departments is not None:
        if not allowed_departments:
            return []
        conditions.append("department IN %(departments)s")
        values["departments"] = tuple(allowed_departments)

    if status:
        conditions.append("status = %(status)s")
        values["status"] = status

    condition_str = " AND ".join(conditions)
    if condition_str:
        condition_str = " AND " + condition_str

    return frappe.db.sql(f"""
        SELECT shift, COUNT(*) count
        FROM `tabAttendance`
        WHERE attendance_date BETWEEN %(from_date)s AND %(to_date)s
        {condition_str}
        GROUP BY shift
    """, values, as_dict=1)


@frappe.whitelist()
def get_overall_attendance(from_date, to_date, shift=None, department=None):

    conditions = []
    filters = {
        "from_date": from_date,
        "to_date": to_date
    }

    allowed_departments = get_allowed_departments()

    if allowed_departments is not None:
        if not allowed_departments:
            return []
        conditions.append("department IN %(departments)s")
        filters["departments"] = tuple(allowed_departments)

    if shift:
        conditions.append("shift = %(shift)s")
        filters["shift"] = shift

    if department:
        conditions.append("department = %(department)s")
        filters["department"] = department

    condition_str = " AND ".join(conditions)
    if condition_str:
        condition_str = " AND " + condition_str

    data = frappe.db.sql(f"""
        SELECT
            company,
            department,
            shift,
            SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) AS present_count,
            SUM(CASE WHEN status IN ('Absent','Leave','LOP') THEN 1 ELSE 0 END) AS absent_count
        FROM `tabAttendance`
        WHERE attendance_date BETWEEN %(from_date)s AND %(to_date)s
        {condition_str}
        GROUP BY company, department, shift
        ORDER BY company, department, shift
    """, filters, as_dict=1)

    for d in data:
        total = d.present_count + d.absent_count
        d.absent_percent = round((d.absent_count / total) * 100, 2) if total else 0

    return data

def get_allowed_departments():
    user = frappe.session.user

    if "HR User" in frappe.get_roles(user):
        return None  

    if "HOD" in frappe.get_roles(user):

        departments = set()

        emp = frappe.db.get_value("Employee", {"user_id": user}, "department")
        if emp:
            departments.add(emp)

        perms = frappe.get_all(
            "User Permission",
            filters={
                "user": user,
                "allow": "Department"
            },
            pluck="for_value"
        )

        for d in perms:
            departments.add(d)

        return list(departments)

    return []
