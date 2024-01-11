import frappe
from frappe.model.document import Document,DocStatus

class LibraryTransaction(Document):

    def before_submit(self):
        
        if self.type == 'Issue':
            self.validate_issue()
            self.validate_maximum_limit()
            # set the article status to be Issued
            article = frappe.get_doc('Article', self.article)
            article.status = 'Issued'
            article.save()

        elif self.type == 'Return':
            self.validate_return()
            # set the article status to be Available
            article = frappe.get_doc('Article', self.article)
            article.status = 'Available'
            article.save()
            
        frappe.msgprint(msg=f"Successfully {self.type}ed Book",title="Success",indicator="green")

    def validate_issue(self):
        self.validate_membership()
        article = frappe.get_doc('Article', self.article)
        # article cannot be issued if it is already issued
        if article.status == 'Issued':
            frappe.throw('Article is already issued by another member')

    def validate_maximum_limit(self):
        max_articles = frappe.db.get_single_value("Library Setting","max_articles")

        count = frappe.db.count("Library Transaction",{
            "library_member" : self.library_member,
            "Type" : "Issue",
            "docstatus" : DocStatus.submitted()
        })
        
        if count >= max_articles:
            frappe.throw("Maximum Limit reached for issuing articles!!")

    def validate_return(self):
        article = frappe.get_doc('Article', self.article)
        # article cannot be returned if it is not issued first
        if article.status == 'Available':
            frappe.throw('Article cannot be returned without being issued first')

    def validate_membership(self):
        # check if a valid membership exist for this library member
        
        # date of return or issue :  form_date < date <= to_date
        
        valid_membership = frappe.db.exists(
            'Library Membership',
            {
                'library_member': self.library_member,
                'docstatus': DocStatus.submitted(),
                'from_date': ('<', self.date),
                'to_date': ('>=', self.date),
            },
        )
        if not valid_membership:
            frappe.throw('The member does not have a valid membership')