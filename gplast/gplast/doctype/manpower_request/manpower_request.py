# Copyright (c) 2023, Teampro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import date
from frappe.utils import nowdate

class ManpowerRequest(Document):
    pass

    def on_update(self):
        if self.workflow_state == "Approved":
            if not self.approve_date:
                self.approve_date = nowdate()
                self.save()

    # def validate(self):
    #     vacancy_count = int(self.vacancy_count) if self.vacancy_count else 0
    #     no_of_vacancy = int(self.no_of_vacancy) if self.no_of_vacancy else 0
    #     if (vacancy_count):
    #             if (vacancy_count > no_of_vacancy):
    #                 frappe.throw("'Vacancy Count' must less than 'No. of vacancy'")

# @frappe.whitelist()
# def get_department_set_emp(user):
#     return frappe.db.get_value('Employee',{'user_id':user},'department')

@frappe.whitelist()
def get_department(user):
    # return frappe.db.get_value('Employee',{'user_id':user},'department')
    deps = frappe.db.get_all(
        "User Permission",
        filters={
            "user": user,
            "allow": "Department"
        },
        fields=["for_value"],
        pluck="for_value"     
    )
    return deps

@frappe.whitelist()
def get_employee(user):
    return frappe.db.get_value('Employee',{'user_id':user},'name')
@frappe.whitelist()
def count_the_job_requisition(department):
    start_of_year = date.today().replace(month=1, day=1)
    return frappe.db.count('Job Requisition', {
        'department': department,
        'creation': (">=", start_of_year)
    })


@frappe.whitelist()
def get_left_employees(department):
    start_of_year = date.today().replace(month=1, day=1)
    job_requisition_documents = frappe.db.get_all(
        'Job Requisition',
        filters={
            'department': department,
            'creation': (">=", start_of_year)
        },
        fields=['creation'],
        order_by='creation ASC',
        limit=1
    )
    if job_requisition_documents:
        creation_date = job_requisition_documents[0].creation
        return frappe.db.count('Employee', {
            'department': department,
            'status': 'Left',
            'relieving_date': (">=", creation_date)
        })
    return 0

@frappe.whitelist()
def get_left_employees_list(department):
    return frappe.db.get_list('Employee', {
            'department': department,
            'status': 'Left'
        },pluck='name',)

@frappe.whitelist()
def get_designation_code(job_id):
    data = frappe.db.get_all(
        'Job Requisition',
        filters={"name": job_id},
        fields=['designation_code', 'designation', 'department', 'no_of_positions','reason']
    )

    if data:
        return data[0]    
    return {}
    # return frappe.db.get_all('Job Requisition', {"name" : job_id}, ['designation_code',"designation","department","no_of_positions"])

@frappe.whitelist()
def get_designation_code_from_left(employee_id_due):
    data = frappe.db.get_all(
        'Employee',
        filters={"name": employee_id_due , 'status':"Left"},
        fields=['designation_code', 'designation', 'department']
    )

    if data:
        return data[0]    
    return {}

@frappe.whitelist()
def get_sub_designation_codes():
    return frappe.db.get_list(
        "Sub Designation",
        {},
        pluck="designation_code"
    )