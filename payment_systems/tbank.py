from payment_systems import flatinn
import settings, logger, db
import requests
import hashlib
import json


def tbank_status(payment: dict) -> list:
    """ GET T-BANK payment STATUS """

    transaction_id = payment.get('transaction', None)
    payment_id = payment.get('payment_id', None)
    logger.logging(text=f"T-BANK payment(#{payment_id}) with transaction: {transaction_id}", log_type="info")

    if payment_id and transaction_id:
        try:

            Token_data = settings.TBANK_PASSWORD + str(transaction_id) + settings.TBANK_TERMINAL_KEY
            Token = hashlib.sha256(Token_data.encode('utf-8')).hexdigest()
            data = json.dumps({
                "TerminalKey": settings.TBANK_TERMINAL_KEY,
                "PaymentId": int(transaction_id),
                "Token": Token
            }, separators=(',', ':'))

            response = requests.post(
                url=settings.TBANK_KASSA_URL,
                data=data,
                headers={"Content-Type": "application/json"}
            )

            data_return = response.json()
            logger.logging(text=f"Payment(#{payment_id}) response: {data_return}", log_type="error")

            if data_return.get('Status', None):
                payment_status = data_return.get('Status').lower().replace('_', '-')
                logger.logging(text=f"Status for payment(#{payment_id}) is {payment_status}", log_type="info")
                update = flatinn.update_state(payment_id=payment_id, status=payment_status, payment=payment)

                if update:
                    return update
            else:
                logger.logging(
                    text=f"Failed to get status for payment(#{payment_id}). T-Bank response: {data_return}\n",
                    log_type="error"
                )
        except Exception as error:
            logger.logging(text=f"Payment(#{payment_id}) error: {error}\n", log_type="error")
    else:
        logger.logging(text=f"Payment hasn't payment_id or transaction_id: {payment}\n", log_type="error")
    return [False, None]
