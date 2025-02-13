from yookassa import Configuration, Payment
import settings, logger, db


def yookassa_status(payment: dict) -> list:
    """ GET YOOKASSA payment STATUS """

    transaction_id = payment.get('transaction', None)
    payment_id = payment.get('payment_id', None)
    logger.logging(text=f"Yookassa payment(#{payment_id}) with transaction: {transaction_id}", log_type="info")

    if payment_id and transaction_id:
        try:
            transaction_status = Payment.find_one(transaction_id).status

            if transaction_status:
                payment_status = transaction_status.lower()
                logger.logging(text=f"Status for payment(#{payment_id}) is {payment_status}", log_type="info")

                if payment_status != payment.get('state', None):
                    logger.logging(text=f"Status for payment(#{payment_id}) has CHANGED", log_type="info")
                    notes = f"Смена статуса: {payment.get('state', None)} -> {payment_status}"
                    selector = [payment_id, payment_status, notes, settings.SERVICE_ID, settings.LANGUAGE]
                    update = db.update_data(db_function='payment_update_json', selector_list=selector)
                    logger.logging(text=f"UPDATE payment(#{payment_id}): {update}", log_type="info")
                    if update and update.get('success', None):
                        success = update.get('success', None)
                        logger.logging(text=f"CHANGE payment(#{payment_id}) STATE: {update}\n", log_type="success")
                        return [success, payment_status]
                    elif update:
                        description = update.get('description', None)
                    else:
                        description = 'DATABASE FAILED'
                    logger.logging(text=f"NOT CHANGE payment(#{payment_id}) STATE: {update}\n", log_type="critical")
                    return [description, payment_status]
                else:
                    logger.logging(text=f"Status for payment(#{payment_id}) has NOT changed\n", log_type="info")
            else:
                logger.logging(
                    text=f"Failed to get status for payment(#{payment_id}). Yookassa status: {transaction_status}\n",
                    log_type="error"
                )
        except Exception as error:
            logger.logging(text=f"Payment(#{payment_id}) error: {error}\n", log_type="error")
    else:
        logger.logging(text=f"Payment hasn't payment_id or transaction_id: {payment}\n", log_type="error")
    return [False, None]


Configuration.account_id = settings.YOOKASSA_ACCOUNT_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY
