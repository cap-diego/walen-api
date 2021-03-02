
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

PAYMENT_STATUS_PENDING = 'pen'
PAYMENT_STATUS_FAILED = 'fld'
PAYMENT_STATUS_RESERVED = 'rsv'
PAYMENT_STATUS_CAPTURED = 'cap'

PAYMENT_STATUS_CHOICES = (
    (PAYMENT_STATUS_PENDING, 'pending'),
    (PAYMENT_STATUS_FAILED, 'failed'),
    (PAYMENT_STATUS_RESERVED, 'reserved'),
    (PAYMENT_STATUS_CAPTURED, 'captured')
)

SHIPMENT_STATUS_AWAITING_PAYMENT = 'awp' # Estado inicial, todavia no se realizo reserva ni captura
SHIPMENT_STATUS_PENDING = 'pen' # Cuando se realizo la captura de la IndPurch y su Purchase tiene clients_left == 0
SHIPMENT_STATUS_AWAITING_PURCHASE_COMPLETITION = 'apc' # Cuando se realiza la captura
SHIPMENT_STATUS_DISPATCHED = 'dis' # Cuando sale el envio
SHIPMENT_STATUS_DELIVERED = 'del' # Cuando se entrega el pedido
SHIPMENT_STATUS_ABORTED = 'abr' # Cuando se cancela su purchase

SHIPMENT_STATUS_CHOICES = (
    (SHIPMENT_STATUS_AWAITING_PAYMENT, 'awaiting-payment'),
    (SHIPMENT_STATUS_PENDING, 'pending'),
    (SHIPMENT_STATUS_AWAITING_PURCHASE_COMPLETITION, 'awaiting-purchase-completition'),
    (SHIPMENT_STATUS_DISPATCHED, 'dispatched'),
    (SHIPMENT_STATUS_DELIVERED, 'delivered'),
    (SHIPMENT_STATUS_ABORTED, 'aborted')
)

PAYMENT_VENDOR_MP = 'mercadopago'
PAYMENT_VENDOR_CHOICES = (
    (PAYMENT_VENDOR_MP, 'Mercado Pago'),
)