#****************************************************************************
#   COLLECTION STATUS
#****************************************************************************
COLLECTION_STATUS = (
    (1, 'Collection Expected'),
    (2, 'Still Collecting'),
    (3, 'Collected'),
)

PARTIAL_COLLECTION_STATUS = (
    (1, 'Collection Expected'),
    (2, 'Collected'),
)

#****************************************************************************
#   PAYMENT TYPE
#****************************************************************************
PAYMENT_TYPE = (
    (1, 'Cash'),
    (2, 'Card'),
    (3, 'Cheque'),
    (4, 'Demand Draft'),
    (5, 'Net Banking'),
)

#****************************************************************************
#   INVOICE/BILLING TERMS
#****************************************************************************
PAYMENT_DAYS = (
    (1, 'Due Immediately'),
    (2, '10 Days'),
    (3, '20 Days'),
    (4, '30 Days'),
    (5, '60 Days'),
    (6, '90 Days'),
    # (7, 'Custom'),
)

invoice_payment_days = (
    (1, 'Due Immediately'),
    (2, '10 Days'),
    (3, '20 Days'),
    (4, '30 Days'),
    (5, '60 Days'),
    (6, '90 Days'),
    (7, 'Custom'),
)

#****************************************************************************
#   PREFERRED PAYMENT TYPES
#****************************************************************************
PREFERRED_PAYMENT_TYPE = (
    (0, 'Any'),
    (1, 'Cash'),
    (2, 'Card'),
    (3, 'Cheque'),
    (4, 'Net Banking'),
)

#****************************************************************************
#   DELIVERY TYPE
#****************************************************************************
PREFERRED_DELIVERY = (
    (0, 'Any'),
    (1, 'Print Later'),
    (2, 'Send Later'),
)

#****************************************************************************
#   FREQUENCY
#****************************************************************************

INVOICE_FREQUENCY = (
    (0, 'Weekly'),
    (1, 'Monthly'),
    (2, 'Quarterly'),
    (3, 'Half yearly'),
    (4, 'Yearly'),
)


#****************************************************************************
#   PAYMENT STATUS
#****************************************************************************

PAYMENT_STATUS = (
    (0, 'Due'),
    (1, 'Over Due By'),
    (2, 'Paid'),
    # (3, 'Send Mail'),
)

purchse_status = (
    (0, 'Due'),
    (1, 'Drafted'),
    (2, 'Cancelled'),
    (3, 'Send Mail'),
)

purchase_entry_status = (
    (0, 'Due'),
    (1, 'Over Due By'),
    (2, 'Drafted'),
    (3, 'Paid'),
    (4, 'Partially Paid'),
)