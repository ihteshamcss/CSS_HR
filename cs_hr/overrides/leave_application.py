import frappe

from frappe import _
from frappe.utils import flt, cint

from hrms.hr.doctype.leave_application.leave_application import (
    LeaveApplication,
    get_leave_balance_on,
    get_number_of_leave_days,
    is_lwp,
)


class CustomLeaveApplication(LeaveApplication):

    def get_balance_deducted_from(self):
        """
        Return the Leave Type whose balance should actually be consumed.

        Example:

            Ex-Pakistan Leave
                ->
            Leave on Full Pay(LFP) Faculty
        """

        deduct_from = frappe.db.get_value(
            "Leave Type",
            self.leave_type,
            "custom_deduct_from_leave_type",
        )

        return deduct_from or self.leave_type


    def is_dependent_leave(self):
        """
        Return True if this Leave Type consumes another Leave Type's balance.
        """

        return bool(
            frappe.db.get_value(
                "Leave Type",
                self.leave_type,
                "custom_deduct_from_leave_type",
            )
        )


    def set_balance_deducted_from(self):
        """
        Store the actual parent/source Leave Type.
        """

        self.custom_balance_deducted_from = (
            self.get_balance_deducted_from()
        )


    def validate(self):
        """
        Set the dependent/source Leave Type before standard validation.
        """

        self.set_balance_deducted_from()

        super().validate()


    def validate_balance_leaves(self):
        """
        Validate balance against the parent Leave Type.

        Example:

            Application Leave Type:
                Ex-Pakistan Leave

            Balance checked:
                Leave on Full Pay(LFP) Faculty
        """

        precision = (
            cint(
                frappe.db.get_single_value(
                    "System Settings",
                    "float_precision",
                )
            )
            or 2
        )

        # ---------------------------------------------------------
        # Calculate requested leave days using the actual
        # Leave Application Leave Type.
        #
        # IMPORTANT:
        # HRMS v14.21.1 does not support the newer
        # leave_application argument here.
        # ---------------------------------------------------------

        if self.from_date and self.to_date:

            self.total_leave_days = get_number_of_leave_days(
                self.employee,
                self.leave_type,
                self.from_date,
                self.to_date,
                self.half_day,
                self.half_day_date,
            )

            if self.total_leave_days <= 0:
                frappe.throw(
                    _(
                        "The day(s) on which you are applying "
                        "for leave are holidays. You need not "
                        "apply for leave."
                    )
                )

        # ---------------------------------------------------------
        # Determine which Leave Type owns the balance.
        # ---------------------------------------------------------

        balance_leave_type = self.get_balance_deducted_from()

        # ---------------------------------------------------------
        # If the parent itself is LWP, there is no balance
        # validation required.
        # ---------------------------------------------------------

        if is_lwp(balance_leave_type):
            return

        # ---------------------------------------------------------
        # Get balance from PARENT Leave Type.
        #
        # Example:
        #
        # Ex-Pakistan Leave = application type
        # LFP Faculty       = balance type
        # ---------------------------------------------------------

        leave_balance = get_leave_balance_on(
            self.employee,
            balance_leave_type,
            self.from_date,
            self.to_date,
            consider_all_leaves_in_the_allocation_period=True,
            for_consumption=True,
        )

        available_balance = flt(
            leave_balance.get(
                "leave_balance_for_consumption"
            ),
            precision,
        )

        # Display parent balance in:
        # "Leave Balance Before Application"
        self.leave_balance = available_balance

        # ---------------------------------------------------------
        # Validate against PARENT balance.
        # ---------------------------------------------------------

        if (
            self.status != "Rejected"
            and (
                available_balance < self.total_leave_days
                or not available_balance
            )
        ):
            frappe.throw(
                _(
                    "Insufficient balance in {0}. "
                    "Available: {1} days. "
                    "Requested: {2} days."
                ).format(
                    frappe.bold(balance_leave_type),
                    available_balance,
                    self.total_leave_days,
                )
            )


    def create_leave_ledger_entry(self, submit=True):
        """
        Create ledger entries for both:

        1. The actual Leave Application Leave Type
        2. The configured parent/source Leave Type

        Example:

            Ex-Pakistan Leave       -5
            LFP Faculty             -5

        If there is no parent Leave Type configured,
        standard HRMS behavior is retained.

        On cancellation, HRMS deletes both entries because
        both use the same transaction name.
        """

        balance_leave_type = self.get_balance_deducted_from()

        # ---------------------------------------------------------
        # Normal Leave Type
        #
        # No dependency -> completely standard HRMS behavior.
        # ---------------------------------------------------------

        if balance_leave_type == self.leave_type:
            return super().create_leave_ledger_entry(
                submit=submit
            )

        # ---------------------------------------------------------
        # FIRST LEDGER
        #
        # Standard HRMS creates:
        #
        # Ex-Pakistan Leave = -5
        # ---------------------------------------------------------

        super().create_leave_ledger_entry(
            submit=submit
        )

        # ---------------------------------------------------------
        # SECOND LEDGER
        #
        # Temporarily use the parent Leave Type so that HRMS's
        # own ledger/allocation logic creates:
        #
        # LFP Faculty = -5
        # ---------------------------------------------------------

        original_leave_type = self.leave_type

        try:

            self.leave_type = balance_leave_type

            super().create_leave_ledger_entry(
                submit=submit
            )

        finally:

            # Restore actual Leave Application Leave Type.
            self.leave_type = original_leave_type




# import frappe

# from frappe import _
# from frappe.utils import flt

# from hrms.hr.doctype.leave_application.leave_application import (
#     LeaveApplication,
#     get_leave_balance_on,
#     is_lwp,
# )


# class CustomLeaveApplication(LeaveApplication):

#     def get_balance_deducted_from(self):
#         """
#         Return the Leave Type whose balance should be consumed.

#         Example:

#         Ex-Pakistan Leave
#             -> Leave on Full Pay(LFP) Faculty

#         If no mapping is configured, use the application's
#         own Leave Type.
#         """

#         deduct_from = frappe.db.get_value(
#             "Leave Type",
#             self.leave_type,
#             "custom_deduct_from_leave_type",
#         )

#         return deduct_from or self.leave_type


#     def set_balance_deducted_from(self):
#         """
#         Store the Leave Type whose balance is being consumed.
#         """

#         self.custom_balance_deducted_from = (
#             self.get_balance_deducted_from()
#         )


#     def validate(self):
#         """
#         Set the linked Leave Type before standard validation.
#         """

#         self.set_balance_deducted_from()

#         super().validate()


#     def validate_balance_leaves(self):
#         """
#         Validate the balance against the configured
#         source Leave Type.

#         Example:

#         Application:
#             Ex-Pakistan Leave

#         Balance validation:
#             Leave on Full Pay(LFP) Faculty
#         """

#         balance_leave_type = self.get_balance_deducted_from()

#         # ---------------------------------------------------------
#         # Calculate total leave days using the application's
#         # Leave Type.
#         #
#         # We deliberately do NOT change self.leave_type here,
#         # because the application itself remains Ex-Pakistan Leave.
#         # ---------------------------------------------------------

#         if self.from_date and self.to_date:

#             from hrms.hr.doctype.leave_application.leave_application import (
#                 get_number_of_leave_days,
#             )

#             self.total_leave_days = get_number_of_leave_days(
#                 self.employee,
#                 self.leave_type,
#                 self.from_date,
#                 self.to_date,
#                 self.half_day,
#                 self.half_day_date,
#             )

#             if self.total_leave_days <= 0:
#                 frappe.throw(
#                     _(
#                         "The day(s) on which you are applying "
#                         "for leave are holidays. You need not "
#                         "apply for leave."
#                     )
#                 )

#         # ---------------------------------------------------------
#         # LWP behavior
#         # ---------------------------------------------------------

#         if is_lwp(balance_leave_type):
#             return

#         # ---------------------------------------------------------
#         # Get balance from the linked Leave Type
#         # ---------------------------------------------------------

#         leave_balance = get_leave_balance_on(
#             self.employee,
#             balance_leave_type,
#             self.from_date,
#             self.to_date,
#             consider_all_leaves_in_the_allocation_period=True,
#             for_consumption=True,
#         )

#         precision = (
#             frappe.get_precision(
#                 "Leave Application",
#                 "leave_balance",
#             )
#             or 2
#         )

#         available_balance = flt(
#             leave_balance.get(
#                 "leave_balance_for_consumption"
#             ),
#             precision,
#         )

#         # "Leave Balance Before Application"
#         self.leave_balance = available_balance


#         if (
#             self.status != "Rejected"
#             and (
#                 available_balance < self.total_leave_days
#                 or not available_balance
#             )
#         ):
#             frappe.throw(
#                 _(
#                     "Insufficient balance in {0}. "
#                     "Available: {1} days. "
#                     "Requested: {2} days."
#                 ).format(
#                     frappe.bold(balance_leave_type),
#                     available_balance,
#                     self.total_leave_days,
#                 )
#             )


#     def create_leave_ledger_entry(self, submit=True):
#         """
#         Create TWO Leave Ledger Entries when a source Leave Type
#         is configured.

#         Example:

#             Leave Application:
#                 Ex-Pakistan Leave

#             Ledger 1:
#                 Ex-Pakistan Leave = -5

#             Ledger 2:
#                 Leave on Full Pay(LFP) Faculty = -5

#         If no source Leave Type is configured, standard HRMS
#         behavior is retained.

#         Cancellation is also handled by standard HRMS because
#         both entries use the same Leave Application transaction
#         name.
#         """

#         balance_leave_type = self.get_balance_deducted_from()


#         if balance_leave_type == self.leave_type:
#             return super().create_leave_ledger_entry(
#                 submit=submit
#             )


#         super().create_leave_ledger_entry(
#             submit=submit
#         )

#         original_leave_type = self.leave_type

#         try:

#             self.leave_type = balance_leave_type

#             super().create_leave_ledger_entry(
#                 submit=submit
#             )

#         finally:

#             self.leave_type = original_leave_type

