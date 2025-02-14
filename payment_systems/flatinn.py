import settings, logger, db


def update_state(payment_id, status, payment):
    """ UPDATE PAYMENT in FLAT INN """

    if status != payment.get('state', None):
        logger.logging(text=f"Status for payment(#{payment_id}) has CHANGED", log_type="info")
        notes = f"Смена статуса: {payment.get('state', None)} -> {status}"
        selector = [payment_id, status, notes, settings.SERVICE_ID, settings.LANGUAGE]
        update = db.update_data(db_function='payment_update_json', selector_list=selector)
        logger.logging(text=f"UPDATE payment(#{payment_id}): {update}", log_type="info")
        if update and update.get('success', None):
            success = update.get('success', None)
            logger.logging(text=f"CHANGE payment(#{payment_id}) STATE: {update}\n", log_type="success")
            return [success, status]
        elif update:
            description = update.get('description', None)
        else:
            description = 'DATABASE FAILED'
        logger.logging(text=f"NOT CHANGE payment(#{payment_id}) STATE: {update}\n", log_type="critical")
        return [description, status]
    else:
        logger.logging(text=f"Status for payment(#{payment_id}) has NOT changed\n", log_type="info")
        return None
