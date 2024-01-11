import frappe
from frappe.model.document import Document, DocStatus


class LibraryTransaction(Document):
   
    def before_submit(self):
        if self.type == "Issue":
            self.validate_issue()
            self.validate_maximum_limit()

            article = frappe.get_doc("Article", self.article)

            article.quantity -= 1

            # set the article status to be Issued
            if article.quantity <= 0:
                article.status = "Issued"

            article.save()

        elif self.type == "Return":
            self.validate_return()

            article = frappe.get_doc("Article", self.article)

            article.quantity += 1

            # set the article status to be Available
            if article.quantity == 0:
                article.status = "Available"

            article.save()

    def validate_issue(self):
        self.validate_membership()
        article = frappe.get_doc("Article", self.article)

        # All Article's copy had been issued
        if article.status == "Issued":
            frappe.throw("Currently Article Is Not Available.")

    def validate_maximum_limit(self):
        max_articles = frappe.db.get_single_value("Library Setting", "max_articles")

        count = frappe.db.count(
            "Library Transaction",
            {
                "library_member": self.library_member,
                "Type": "Issue",
                "docstatus": DocStatus.submitted(),
            },
        )

        if count >= max_articles:
            frappe.throw("Maximum Limit reached for issuing articles!!")

    def validate_return(self):
        self.validate_membership()

    def validate_membership(self):
        # check if a valid membership exist for this library member

        # date of return or issue :  form_date < date <= to_date
        # date of return :  form_date < date
        # and if return date >= to_date fine charges. also if return date is (Issued Date > 30) then also fine charges (Feature left)

        filters = {}

        if self.type == "Issue":
            
            filters = {
                "library_member": self.library_member,
                "docstatus": DocStatus.submitted(),
                "from_date": ("<", self.date),
                "to_date": (">=", self.date),
            }
            
        else:
             filters = {
                "library_member": self.library_member,
                "docstatus": DocStatus.submitted(),
                "from_date": ("<", self.date),
            }

        valid_membership = frappe.db.exists("Library Membership",filters)
        
        if not valid_membership:
            frappe.throw("The member does not have a valid membership")

    def on_submit(self):
        frappe.msgprint(
            msg=f"Successfully {'Issued' if self.type == 'Issue' else 'Returned'} Book",
            title="Success",
            indicator="green",
        )
