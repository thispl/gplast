# Copyright (c) 2025, Teampro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class RevisionSummary(Document):
	pass



@frappe.whitelist()
def get_salary_details(employee):
# def get_salary_details():
    # employee ='123443215678'
    if not employee:
        return []

    documents = frappe.db.get_all('Salary Increment', {'employee': employee,'docstatus':1}, ['*'])

    salary_details_list = []

    for doc in documents:
        if doc.increment_by =='Percentage':
            salary_details = {
            'basic': doc.basic,
            'cca':doc.cca,
            'house_rent_allowance': doc.house_rent_allowance,
            'special_allowance': doc.special_allowance,
            'conveyance_allowance': doc.conveyance_allowance,
            'medical_allowances': doc.medical_allowances,
            'shift_allowance': doc.shift_allowance,
            'other_allowance': doc.other_allowance,
            'uniform_allowance': doc.uniform_allowance,
            'magazine_allowances': doc.magazine_allowances,
            'reference_document':doc.name,
            'salary_increment_date':getdate(doc.modified),
            'increment_type':doc.increment_by,
            'gross_salary':doc.salary_total,
            'increment_amount':doc.revised_total,
            # 'revised_basic':doc.revise_basic,
            # 'revised_cca':doc.revise_cca,
            # 'revised_house_rent_allowance': doc.revise_hra,
            # 'revised_special_allowance': doc.revise_special_allowance,
            # 'revised_conveyance_allowance': doc.revise_conveyance_allowance,
            # 'revised_medical_allowances': doc.revise_allowances,
            # 'revised_shift_allowance': doc.revise_shift_allowance,
            # 'revised_other_allowance': doc.revise_other_allowance,
            # 'revised_uniform_allowance': doc.revise_uniform_allowance,
            # 'revised_magazine_allowances': doc.revise_magazine_allowance,
            # 'revised_gross_salary':doc.revise_total
            'revised_basic':doc.revised_basic,
            'revised_cca':doc.revised_cca,
            'revised_house_rent_allowance': doc.revised_hra,
            'revised_special_allowance': doc.revised_special_allowance,
            'revised_conveyance_allowance': doc.revised_conveyance_allowance,
            'revised_medical_allowances': doc.revised_allowances,
            'revised_shift_allowance': doc.revised_shift_allowance,
            'revised_other_allowance': doc.revised_other_allowance,
            'revised_uniform_allowance': doc.revised_uniform_allowance,
            'revised_magazine_allowances': doc.revised_magazine_allowance,
            'revised_gross_salary':doc.revise_total,
            'revise_basic_':doc.revise_basic,
            'revise_cca':doc.revise_cca,
            'revise_house_rent_allowance': doc.revise_hra,
            'revise_special_allowance': doc.revise_special_allowance,
            'revise_conveyance_allowance': doc.revise_conveyance_allowance,
            'revise_medical_allowances': doc.revise_allowances,
            'revise_shift_allowance': doc.revise_shift_allowance,
            'revise_other_allowance': doc.revise_other_allowance,
            'revise_uniform_allowance': doc.revise_uniform_allowance,
            'revise_magazine_allowances': doc.revise_magazine_allowance
            
        }
        elif doc.increment_by =='Amount':
            salary_details = {
            'basic': doc.basic,
            'cca':doc.cca,
            'house_rent_allowance': doc.house_rent_allowance,
            'special_allowance': doc.special_allowance,
            'conveyance_allowance': doc.conveyance_allowance,
            'medical_allowances': doc.medical_allowances,
            'shift_allowance': doc.shift_allowance,
            'other_allowance': doc.other_allowance,
            'uniform_allowance': doc.uniform_allowance,
            'magazine_allowances': doc.magazine_allowances,
            'reference_document':doc.name,
            'salary_increment_date':getdate(doc.modified),
            'increment_type':doc.increment_by,
            'gross_salary':doc.salary_total,
            'increment_amount':doc.revised_total,
            'revised_basic':doc.revised_basic,
            'revised_cca':doc.revised_cca,
            'revised_house_rent_allowance': doc.revised_hra,
            'revised_special_allowance': doc.revised_special_allowance,
            'revised_conveyance_allowance': doc.revised_conveyance_allowance,
            'revised_medical_allowances': doc.revised_allowances,
            'revised_shift_allowance': doc.revised_shift_allowance,
            'revised_other_allowance': doc.revised_other_allowance,
            'revised_uniform_allowance': doc.revised_uniform_allowance,
            'revised_magazine_allowances': doc.revised_magazine_allowance,
            'revised_gross_salary':doc.revise_total,
            'revise_basic_':doc.revise_basic,
            'revise_cca':doc.revise_cca,
            'revise_house_rent_allowance': doc.revise_hra,
            'revise_special_allowance': doc.revise_special_allowance,
            'revise_conveyance_allowance': doc.revise_conveyance_allowance,
            'revise_medical_allowances': doc.revise_allowances,
            'revise_shift_allowance': doc.revise_shift_allowance,
            'revise_other_allowance': doc.revise_other_allowance,
            'revise_uniform_allowance': doc.revise_uniform_allowance,
            'revise_magazine_allowances': doc.revise_magazine_allowance
            
        }
        salary_details_list.append(salary_details)

    return salary_details_list
