// Copyright (c) 2024, AbdeTion and contributors
// For license information, please see license.txt

frappe.ui.form.on("Library Member", {
	
    refresh : function (form) {
        
        form.add_custom_button('Create Membership',() => {
            frappe.new_doc("Library Membership",{
                library_member: form.doc.name
            })
        })

        form.add_custom_button("Create Transaction",()=>{
            frappe.new_doc("Library Transaction",{
                library_member:form.doc.name
            })
        })

    }

});