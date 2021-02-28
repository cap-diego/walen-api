
PURCHASE_STATUS_AWAITING_PEERS = 'aws'
PURCHASE_STATUS_PEND_INIT_PAY = 'pip'
PURCHASE_STATUS_COMPLETED = 'cmp'
PURCHASE_STATUS_CANCELLED = 'cnc'

PURCHASE_STATUS_CHOICES = (
    (PURCHASE_STATUS_AWAITING_PEERS, 'awaiting-peers'),
    (PURCHASE_STATUS_PEND_INIT_PAY, 'pending-initial-payment'),
    (PURCHASE_STATUS_COMPLETED, 'completed'),
    (PURCHASE_STATUS_CANCELLED, 'cancelled')
)