# Copyright (c) 2025, Teampro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from dateutil.relativedelta import relativedelta
import calendar
from dateutil.relativedelta import relativedelta
from datetime import datetime

class SalaryIncrement(Document):
	def validate(self):
		if self.increment_by=='Percentage':
			if self.total_percent != None:
				tot=float(self.total_percent)
				if tot>100:
					frappe.throw("Total Percentage should not exceed 100")
				if tot<100:
					frappe.throw("Total Percentage should be equal to 100") 
				if self.total_amount==0:
					frappe.throw("Total amount must be greater than 0") 
			else:
				frappe.throw("Total Percentage should be equal to 100") 
		else:
			if self.revised_total==0:
				frappe.throw("Total amount must be greater than 0") 
	def on_submit(self):
		emp=frappe.get_doc("Employee",self.employee)
		# if self.increment_by=='Amount':
		# 	emp.basic=self.revised_basic
		# 	emp.cca=self.revised_cca
		# 	emp.house_rent_allowance=self.revised_hra
		# 	emp.special_allowance=self.revised_special_allowance
		# 	emp.conveyance_allowance=self.revised_conveyance_allowance
		# 	emp.medical_allowances=self.revised_allowances
		# 	emp.shift_allowance=self.revised_shift_allowance
		# 	emp.other_allowance=self.revised_other_allowance
		# 	emp.arrear=self.revised_arrear_basic
		# 	emp.arrear_hra=self.revised_arrear_hra
		# 	emp.uniform_allowance=self.revised_uniform_allowance
		# 	emp.magazine_allowances=self.revised_magazine_allowance
		# 	emp.salary_total=self.revised_total
		# else:
		emp.basic=self.revise_basic
		emp.cca=self.revise_cca
		emp.house_rent_allowance=self.revise_hra
		emp.special_allowance=self.revise_special_allowance
		emp.conveyance_allowance=self.revise_conveyance_allowance
		emp.medical_allowances=self.revise_allowances
		emp.shift_allowance=self.revise_shift_allowance
		emp.other_allowance=self.revise_other_allowance
		emp.arrear=self.revise_arrear_basic
		emp.arrear_hra=self.revise_arrear_hra
		emp.uniform_allowance=self.revise_uniform_allowance
		emp.magazine_allowances=self.revise_magazine_allowance
		emp.salary_total=self.revise_total
		emp.save()
		if not frappe.db.exists('Revision Summary' ,{'employee':self.employee}):
			rs = frappe.new_doc('Revision Summary')
			rs.employee=self.employee
			rs.save(ignore_permissions=True)
			frappe.db.commit()
		arr = frappe.new_doc('Arrear')
		arr.employee = self.employee
		arr.employee_name = self.employee_name
		arr.salary_increment = self.name
		arr.department = self.department
		arr.designation = self.designation
		incre_month = frappe.db.get_value("Employee",{"name":self.employee},"increment_month")
		arr.increment_month = incre_month
		arr.incremented_by = self.creation 
		if self.increment_by == "Amount":
			increment_amount1 = self.revise_total - self.salary_total
			arr.increment_amount = increment_amount1
		if self.increment_by == "Percentage":
			arr.increment_amount = self.total_amount
		arr.basic_c = self.basic
		arr.hra_c = self.house_rent_allowance
		arr.cca_c = self.cca
		arr.spl_c = self.special_allowance
		arr.other_c = self.other_allowance
		arr.basic_r = self.revise_basic
		arr.hra_r = self.revise_hra
		arr.cca_r = self.revise_cca
		arr.spl_r = self.revise_special_allowance
		arr.other_r = self.revise_other_allowance
		arr.basic_i = arr.basic_r - arr.basic_c
		arr.hra_i = arr.hra_r - arr.hra_c
		arr.cca_i = arr.cca_r - arr.cca_c
		arr.spl_i = arr.spl_r - arr.spl_c
		arr.other_i = arr.other_r - arr.other_c

		
		month_start = arr.increment_month
		if isinstance(month_start, str):
			month_start = datetime.strptime(month_start, "%Y-%m-%d").date()  
		creation_str = self.creation
		creation_dt = datetime.strptime(creation_str, "%Y-%m-%d %H:%M:%S.%f")		        
		month_end = creation_dt.date()
		diff = relativedelta(month_end, month_start)
		diff_months = diff.years * 12 + diff.months

		current = month_start
		arrear_basic_total = 0
		arrear_hra_total = 0
		arrear_cca_total = 0
		arrear_spl_total = 0
		arrear_other_total = 0

		for i in range(diff_months):
			month_start_dt = current.replace(day=1)
			month_end_dt = (month_start_dt + relativedelta(months=1)) - relativedelta(days=1)
			month_start_str = month_start_dt.strftime("%Y-%m-%d")
			month_end_str = month_end_dt.strftime("%Y-%m-%d")
			slip = frappe.db.get_value(
				"Salary Slip",
				{
					"employee": arr.employee,
					"start_date": (">=", month_start_str),
					"end_date": ("<=", month_end_str)
				},
				["name", "total_working_days", "payment_days"],
				as_dict=True
			)

			if slip and slip.total_working_days and slip.payment_days:
				month_arrear_basic = (arr.basic_i / slip.total_working_days) * slip.payment_days
				arrear_basic_total += month_arrear_basic
				month_arrear_hra = (arr.hra_i / slip.total_working_days) * slip.payment_days
				arrear_hra_total += month_arrear_hra
				month_arrear_cca = (arr.cca_i / slip.total_working_days) * slip.payment_days
				arrear_cca_total += month_arrear_cca
				month_arrear_spl = (arr.spl_i / slip.total_working_days) * slip.payment_days
				arrear_spl_total += month_arrear_spl
				month_arrear_other = (arr.other_i / slip.total_working_days) * slip.payment_days
				arrear_other_total += month_arrear_other

			current = current + relativedelta(months=1)

		arr.arrear_basic = arrear_basic_total
		arr.arrear_hra = arrear_hra_total
		arr.arrear_cca = arrear_cca_total
		arr.arrear_spl = arrear_spl_total
		arr.arrear_other = arrear_other_total
		arr.arrear_pf = ( arr.arrear_basic + arr.arrear_cca + arr.arrear_spl ) * 0.12
		arr.arrear_esi = ( arr.arrear_basic + arr.arrear_cca + arr.arrear_spl + arr.arrear_hra + arr.arrear_other ) * 0.0075
		arr.arrear_total = ( arr.arrear_basic + arr.arrear_hra + arr.arrear_cca  + arr.arrear_spl + arr.arrear_other ) - (arr.arrear_pf + arr.arrear_esi)
		arr.save(ignore_permissions=True)
		frappe.db.commit()
		payroll_date = creation_dt.replace(day=1).date()
		if arr.arrear_basic > 0:
			adds = frappe.new_doc('Additional Salary')
			adds.employee = self.employee
			adds.payroll_date = payroll_date
			adds.salary_component = "Basic ARR"
			adds.amount = arr.arrear_basic
			adds.ref_doctype = "Salary Increment"
			adds.ref_docname = self.name
			adds.save(ignore_permissions=True)
			adds.submit()
			frappe.db.commit()
		if arr.arrear_hra > 0:
			adds = frappe.new_doc('Additional Salary')
			adds.employee = self.employee
			adds.payroll_date = payroll_date
			adds.salary_component = "HRA ARR"
			adds.amount = arr.arrear_hra
			adds.ref_doctype = "Salary Increment"
			adds.ref_docname = self.name
			adds.save(ignore_permissions=True)
			adds.submit()
			frappe.db.commit()
		if arr.arrear_cca > 0:
			adds = frappe.new_doc('Additional Salary')
			adds.employee = self.employee
			adds.payroll_date = payroll_date
			adds.salary_component = "CCA Arrear"
			adds.amount = arr.arrear_cca
			adds.ref_doctype = "Salary Increment"
			adds.ref_docname = self.name
			adds.save(ignore_permissions=True)
			adds.submit()
			frappe.db.commit()
		if arr.arrear_spl > 0:
			adds = frappe.new_doc('Additional Salary')
			adds.employee = self.employee
			adds.payroll_date = payroll_date
			adds.salary_component = "Special Arrear"
			adds.amount = arr.arrear_spl
			adds.ref_doctype = "Salary Increment"
			adds.ref_docname = self.name
			adds.save(ignore_permissions=True)
			adds.submit()
			frappe.db.commit()
		if arr.arrear_other > 0:
			adds = frappe.new_doc('Additional Salary')
			adds.employee = self.employee
			adds.payroll_date = payroll_date
			adds.salary_component = "Other Arrear"
			adds.amount = arr.arrear_other
			adds.ref_doctype = "Salary Increment"
			adds.ref_docname = self.name
			adds.save(ignore_permissions=True)
			adds.submit()
			frappe.db.commit()	
		if arr.arrear_pf > 0:
			adds = frappe.new_doc('Additional Salary')
			adds.employee = self.employee
			adds.payroll_date = payroll_date
			adds.salary_component = "Arrear PF"
			adds.amount = arr.arrear_pf
			adds.ref_doctype = "Salary Increment"
			adds.ref_docname = self.name
			adds.save(ignore_permissions=True)
			adds.submit()
			frappe.db.commit()
		if arr.arrear_esi > 0:
			adds = frappe.new_doc('Additional Salary')
			adds.employee = self.employee
			adds.payroll_date = payroll_date
			adds.salary_component = "Arrear ESI"
			adds.amount = arr.arrear_esi
			adds.ref_doctype = "Salary Increment"
			adds.ref_docname = self.name
			adds.save(ignore_permissions=True)
			adds.submit()
			frappe.db.commit()							
	def on_cancel(self):
		emp=frappe.get_doc("Employee",self.employee)
		emp.basic=self.basic
		emp.cca=self.cca
		emp.house_rent_allowance=self.house_rent_allowance
		emp.special_allowance=self.special_allowance
		emp.conveyance_allowance=self.conveyance_allowance
		emp.medical_allowances=self.medical_allowances
		emp.shift_allowance=self.shift_allowance
		emp.other_allowance=self.other_allowance
		emp.arrear=self.arrear_basic
		emp.arrear_hra=self.arrear_hra
		emp.uniform_allowance=self.uniform_allowance
		emp.magazine_allowances=self.magazine_allowances
		emp.salary_total=self.salary_total
		emp.save()
		frappe.db.delete("Arrear", {"salary_increment": self.name})
		frappe.db.commit()
		salary_docs = frappe.get_all(
			"Additional Salary",
			filters={"ref_docname": self.name},
			fields=["name"]
		)

		for doc in salary_docs:
			add_doc = frappe.get_doc("Additional Salary", doc.name)
			if add_doc.docstatus == 1:  
				add_doc.cancel()        

		frappe.db.commit()



