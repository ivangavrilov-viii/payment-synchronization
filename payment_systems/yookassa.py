from yookassa import Configuration, Payment
from payment_systems import flatinn
import settings, logger, db


def yookassa_status(payment: dict) -> list:
    """ GET YOOKASSA payment STATUS """

    # transaction_id = payment.get('transaction', None)
    transaction_id = payment.get('transaction_id', None)
    payment_id = payment.get('payment_id', None)
    logger.logging(text=f"Yookassa payment(#{payment_id}) with transaction: {transaction_id}", log_type="info")

    if payment_id and transaction_id:
        try:
            transaction_status = Payment.find_one(transaction_id).status

            if transaction_status:
                payment_status = transaction_status.lower()
                logger.logging(text=f"Status for payment(#{payment_id}) is {payment_status}", log_type="info")
                update = flatinn.update_state(payment_id=payment_id, status=payment_status, payment=payment)

                if update:
                    return update
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
