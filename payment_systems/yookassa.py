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
                    print(selector)
                    # INSERT FUNC TO SAVE IN DB
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


# update_response = try_except_callproc_request_to_db('payment_update', selector_list, func_name)
# debug_log(f"SUCCESS | Changing DB response is {update_response}", FILE_LOG)
#
# if update_response[0]:
#     debug_log(f"SUCCESS | Payment's (id={payment_id}) status was changed.", FILE_LOG)
#     return [update_response[0], payment_status]
# debug_log(f"FAILED | Payment's (id={payment_id}) status wasn't changed with  comment: {update_response[1]}", FILE_LOG)
# return [update_response[1], payment_status]
