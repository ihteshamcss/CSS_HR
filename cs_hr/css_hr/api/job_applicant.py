import frappe
from frappe import _

def validate_job_application(doc, method):

    email_exists = frappe.db.exists(
        "Job Applicant",
        {
            "job_title": doc.job_title,
            "email_id": doc.email_id,
            "name": ["!=", doc.name]
        }
    )

    cnic_exists = frappe.db.exists(
        "Job Applicant",
        {
            "job_title": doc.job_title,
            "cnic": doc.cnic,
            "name": ["!=", doc.name]
        }
    )

    if email_exists and cnic_exists:
        frappe.throw(
            _("You have already applied for this job using Email <b>{0}</b> and CNIC <b>{1}</b>.")
            .format(doc.email_id, doc.cnic)
        )

    elif email_exists:
        frappe.throw(
            _("You have already applied for this job using Email <b>{0}</b>.")
            .format(doc.email_id)
        )

    elif cnic_exists:
        frappe.throw(
            _("You have already applied for this job using CNIC <b>{0}</b>.")
            .format(doc.cnic)
        )