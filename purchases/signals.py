



def check_if_purchase_finished(sender, **kwargs):
    purchase = kwargs['instance']
    if purchase.is_completed:
        return

    if not purchase.clients_target_reached:
        return
    
    purchase.set_status_completed()
    
    
