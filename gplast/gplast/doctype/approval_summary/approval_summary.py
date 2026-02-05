# # Copyright (c) 2026, Teampro and contributors
# # For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ApprovalSummary(Document):
# 	@frappe.whitelist(allow_guest=True)
# 	def submit_leave_doc(self,doctype,name,workflow_state):
# 		frappe.log_error(doctype,workflow_state)
# 		doc = frappe.get_doc(doctype,name)
# 		if workflow_state == 'Approved':
# 			doc.status = 'Approved'
# 			doc.flags.ignore_permissions = 1
# 			doc.workflow_state = workflow_state
# 			doc.save(ignore_permissions=True)
# 			doc.submit()
# 		elif workflow_state == 'Rejected' and doctype=='Leave Application':
# 			doc.workflow_state = workflow_state
# 			doc.status='Rejected'
# 			doc.save(ignore_permissions=True) 
# 			doc.submit()          
# 		else:
# 			if workflow_state == 'Pending for Manager':
# 				if doc.total_leave_approvers ==1:
# 					doc.workflow_state = 'Approved'
# 					doc.save(ignore_permissions=True)
# 				else:
# 					doc.workflow_state = workflow_state
# 					doc.save(ignore_permissions=True)
# 			# else:
# 			# 	doc.workflow_state = workflow_state
# 			# 	doc.save(ignore_permissions=True)
# 		return "ok"

	@frappe.whitelist(allow_guest=True)
	def submit_leave_doc(self, doctype, name, workflow_state):
		frappe.log_error(doctype, workflow_state)
		doc = frappe.get_doc(doctype, name)

		if workflow_state == 'Approved':
			doc.status = 'Approved'
			doc.flags.ignore_permissions = 1
			doc.workflow_state = 'Approved'
			doc.save(ignore_permissions=True)
			doc.submit()

		elif workflow_state == 'Rejected' and doctype == 'Leave Application':
			doc.workflow_state = 'Rejected'
			doc.status = 'Rejected'
			doc.save(ignore_permissions=True)
			doc.submit()

		else:
			total = doc.total_leave_approvers
			current = workflow_state   # coming from JS

			# Pending for Manager
			if current == 'Pending for Manager':
				if total == 1:
					doc.workflow_state = 'Approved'
					doc.status = 'Approved'
					doc.save(ignore_permissions=True)
					doc.submit()
				else:
					doc.workflow_state = 'Pending for Manager 1'
					doc.save(ignore_permissions=True)

			# Pending for Manager 1
			elif current == 'Pending for Manager 1':
				if total == 2:
					doc.workflow_state = 'Approved'
					doc.status = 'Approved'
					doc.save(ignore_permissions=True)
					doc.submit()
				else:
					doc.workflow_state = 'Pending for Manager 2'
					doc.save(ignore_permissions=True)

			# Pending for Manager 2
			elif current == 'Pending for Manager 2':
				if total == 3:
					doc.workflow_state = 'Approved'
					doc.status = 'Approved'
					doc.save(ignore_permissions=True)
					doc.submit()
				else:
					doc.workflow_state = 'Pending for Manager 3'
					doc.save(ignore_permissions=True)

			# Pending for Manager 3
			elif current == 'Pending for Manager 3':
				doc.workflow_state = 'Approved'
				doc.status = 'Approved'
				doc.save(ignore_permissions=True)
				doc.submit()

			# Fallback (safety)
			else:
				doc.workflow_state = current
				doc.save(ignore_permissions=True)

		return {"workflow_state": doc.workflow_state}

	
	@frappe.whitelist(allow_guest=True)
	def submit_od(self, doctype, name, workflow_state):
		frappe.log_error(doctype, workflow_state)
		doc = frappe.get_doc(doctype, name)

		if workflow_state == 'Approved':
			doc.status = 'Approved'
			doc.flags.ignore_permissions = 1
			doc.workflow_state = 'Approved'
			doc.save(ignore_permissions=True)
			doc.submit()

		elif workflow_state == 'Rejected' and doctype == 'On Duty Application':
			doc.workflow_state = 'Rejected'
			doc.status = 'Rejected'
			doc.save(ignore_permissions=True)
			doc.submit()

		else:
			total = doc.total_leave_approvers
			current = workflow_state   # coming from JS

			# Pending for Manager
			if current == 'Pending for Manager':
				if total == 1:
					doc.workflow_state = 'Approved'
					doc.status = 'Approved'
					doc.save(ignore_permissions=True)
					doc.submit()
				else:
					doc.workflow_state = 'Pending for Manager 1'
					doc.save(ignore_permissions=True)

			# Pending for Manager 1
			elif current == 'Pending for Manager 1':
				if total == 2:
					doc.workflow_state = 'Approved'
					doc.status = 'Approved'
					doc.save(ignore_permissions=True)
					doc.submit()
				else:
					doc.workflow_state = 'Pending for Manager 2'
					doc.save(ignore_permissions=True)

			# Pending for Manager 2
			elif current == 'Pending for Manager 2':
				if total == 3:
					doc.workflow_state = 'Approved'
					doc.status = 'Approved'
					doc.save(ignore_permissions=True)
					doc.submit()
				else:
					doc.workflow_state = 'Pending for Manager 3'
					doc.save(ignore_permissions=True)

			# Pending for Manager 3
			elif current == 'Pending for Manager 3':
				doc.workflow_state = 'Approved'
				doc.status = 'Approved'
				doc.save(ignore_permissions=True)
				doc.submit()

			# Fallback (safety)
			else:
				doc.workflow_state = current
				doc.save(ignore_permissions=True)

		return {"workflow_state": doc.workflow_state}


	
	@frappe.whitelist(allow_guest=True)
	def submit_miss_punch(self, doctype, name, workflow_state):
		frappe.log_error(doctype, workflow_state)
		doc = frappe.get_doc(doctype, name)

		if workflow_state == 'Approved':
			doc.status = 'Approved'
			doc.flags.ignore_permissions = 1
			doc.workflow_state = 'Approved'
			doc.save(ignore_permissions=True)
			doc.submit()

		elif workflow_state == 'Rejected' and doctype == 'Miss Punch Application':
			doc.workflow_state = 'Rejected'
			doc.status = 'Rejected'
			doc.save(ignore_permissions=True)
			doc.submit()

		else:
			total = doc.total_leave_approvers
			current = workflow_state   # coming from JS

			# Pending for Manager
			if current == 'Pending for Manager':
				if total == 1:
					doc.workflow_state = 'Approved'
					doc.status = 'Approved'
					doc.save(ignore_permissions=True)
					doc.submit()
				else:
					doc.workflow_state = 'Pending for Manager 1'
					doc.save(ignore_permissions=True)

			# Pending for Manager 1
			elif current == 'Pending for Manager 1':
				if total == 2:
					doc.workflow_state = 'Approved'
					doc.status = 'Approved'
					doc.save(ignore_permissions=True)
					doc.submit()
				else:
					doc.workflow_state = 'Pending for Manager 2'
					doc.save(ignore_permissions=True)

			# Pending for Manager 2
			elif current == 'Pending for Manager 2':
				if total == 3:
					doc.workflow_state = 'Approved'
					doc.status = 'Approved'
					doc.save(ignore_permissions=True)
					doc.submit()
				else:
					doc.workflow_state = 'Pending for Manager 3'
					doc.save(ignore_permissions=True)

			# Pending for Manager 3
			elif current == 'Pending for Manager 3':
				doc.workflow_state = 'Approved'
				doc.status = 'Approved'
				doc.save(ignore_permissions=True)
				doc.submit()

			# Fallback (safety)
			else:
				doc.workflow_state = current
				doc.save(ignore_permissions=True)

		return {"workflow_state": doc.workflow_state}

	
	
	@frappe.whitelist(allow_guest=True)
	def submit_permission(self, doctype, name, workflow_state):
		frappe.log_error(doctype, workflow_state)
		doc = frappe.get_doc(doctype, name)

		if workflow_state == 'Approved':
			doc.status = 'Approved'
			doc.flags.ignore_permissions = 1
			doc.workflow_state = 'Approved'
			doc.save(ignore_permissions=True)
			doc.submit()

		elif workflow_state == 'Rejected' and doctype == 'Attendance Permission':
			doc.workflow_state = 'Rejected'
			doc.status = 'Rejected'
			doc.save(ignore_permissions=True)
			doc.submit()

		else:
			total = doc.total_leave_approvers
			current = workflow_state   # coming from JS

			# Pending for Manager
			if current == 'Pending for Manager':
				if total == 1:
					doc.workflow_state = 'Approved'
					doc.status = 'Approved'
					doc.save(ignore_permissions=True)
					doc.submit()
				else:
					doc.workflow_state = 'Pending for Manager 1'
					doc.save(ignore_permissions=True)

			# Pending for Manager 1
			elif current == 'Pending for Manager 1':
				if total == 2:
					doc.workflow_state = 'Approved'
					doc.status = 'Approved'
					doc.save(ignore_permissions=True)
					doc.submit()
				else:
					doc.workflow_state = 'Pending for Manager 2'
					doc.save(ignore_permissions=True)

			# Pending for Manager 2
			elif current == 'Pending for Manager 2':
				if total == 3:
					doc.workflow_state = 'Approved'
					doc.status = 'Approved'
					doc.save(ignore_permissions=True)
					doc.submit()
				else:
					doc.workflow_state = 'Pending for Manager 3'
					doc.save(ignore_permissions=True)

			# Pending for Manager 3
			elif current == 'Pending for Manager 3':
				doc.workflow_state = 'Approved'
				doc.status = 'Approved'
				doc.save(ignore_permissions=True)
				doc.submit()

			# Fallback (safety)
			else:
				doc.workflow_state = current
				doc.save(ignore_permissions=True)

		return {"workflow_state": doc.workflow_state}


	@frappe.whitelist(allow_guest=True)
	def submit_overtime(self, doctype, name, workflow_state):
		frappe.log_error(doctype, workflow_state)
		doc = frappe.get_doc(doctype, name)

		if workflow_state == 'Approved':
			doc.status = 'Approved'
			doc.flags.ignore_permissions = 1
			doc.workflow_state = 'Approved'
			doc.save(ignore_permissions=True)
			doc.submit()

		elif workflow_state == 'Rejected' and doctype == 'Over Time':
			doc.workflow_state = 'Rejected'
			doc.status = 'Rejected'
			doc.save(ignore_permissions=True)
			doc.submit()

		else:
			total = doc.total_leave_approvers
			current = workflow_state   # coming from JS

			# Pending for Manager
			if current == 'Pending for Manager':
				if total == 1:
					doc.workflow_state = 'Approved'
					doc.status = 'Approved'
					doc.save(ignore_permissions=True)
					doc.submit()
				else:
					doc.workflow_state = 'Pending for Manager 1'
					doc.save(ignore_permissions=True)

			# Pending for Manager 1
			elif current == 'Pending for Manager 1':
				if total == 2:
					doc.workflow_state = 'Approved'
					doc.status = 'Approved'
					doc.save(ignore_permissions=True)
					doc.submit()
				else:
					doc.workflow_state = 'Pending for Manager 2'
					doc.save(ignore_permissions=True)

			# Pending for Manager 2
			elif current == 'Pending for Manager 2':
				if total == 3:
					doc.workflow_state = 'Approved'
					doc.status = 'Approved'
					doc.save(ignore_permissions=True)
					doc.submit()
				else:
					doc.workflow_state = 'Pending for Manager 3'
					doc.save(ignore_permissions=True)

			# Pending for Manager 3
			elif current == 'Pending for Manager 3':
				doc.workflow_state = 'Approved'
				doc.status = 'Approved'
				doc.save(ignore_permissions=True)
				doc.submit()

			# Fallback (safety)
			else:
				doc.workflow_state = current
				doc.save(ignore_permissions=True)

		return {"workflow_state": doc.workflow_state}