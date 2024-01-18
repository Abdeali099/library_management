# Copyright (c) 2024, AbdeTion and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.document import DocStatus
from frappe import utils

class LibraryMembership(Document):
    
    # check before submitting this document
    
    # If current membership_form's `from date` > already available `to date``
    #  Then new membership can't be created because old one is not expire right now 
    
    def before_submit(self):
        
        exists = frappe.db.exists(
            'Library Membership',
            {
                'library_member' : self.library_member,
                'docstatus':DocStatus.submitted(),	
                'to_date' : (">",self.from_date)
            }
        )
  
        if exists:
            frappe.throw("There is an Active membership for this member")

        # get loan period and compute to_date by adding loan period
        loan_period = frappe.db.get_single_value("Library Setting","loan_period")
        self.to_date = utils.add_days(self.from_date,loan_period or 30)
        

    def on_submit(self):
        frappe.msgprint(msg="Successfully Membership created.",title="Success",indicator="green")