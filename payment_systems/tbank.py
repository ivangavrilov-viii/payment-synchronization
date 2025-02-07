# from .payments_keys import TINKOFF_PASSWORD, TINKOFF_TERMINAL_KEY
# from settings.db import try_except_callproc_request_to_db
# from settings.debug_log import debug_log
# import configparser


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

            Token_data = settings.TINKOFF_PASSWORD + str(transaction_id) + settings.TINKOFF_TERMINAL_KEY
            Token = hashlib.sha256(Token_data.encode('utf-8')).hexdigest()
            data = json.dumps({
                "TerminalKey": settings.TINKOFF_TERMINAL_KEY,
                "PaymentId": int(transaction_id),
                "Token": Token
            }, separators=(',', ':'))

            response = requests.post(
                url=settings.TINKOFF_KASSA_URL,
                data=data,
                headers={"Content-Type": "application/json"}
            )

            data_return = response.json()
            logger.logging(text=f"Payment(#{payment_id}) response: {data_return}", log_type="error")

            if data_return.get('Status', None):
                payment_status = data_return.get('Status').lower().replace('_', '-')
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
                logger.logging(text=f"Failed to get status for payment(#{payment_id}) from T-Bank\n", log_type="error")
        except Exception as error:
            logger.logging(text=f"Payment(#{payment_id}) error: {error}\n", log_type="error")
    else:
        logger.logging(text=f"Payment hasn't payment_id or transaction_id: {payment}\n", log_type="error")
    return [False, None]


# update_response = try_except_callproc_request_to_db('payment_update', selector_list, func_name)
# debug_log(f"SUCCESS | Changing DB response is {update_response}", FILE_LOG)
#
# if update_response[0]:
#     debug_log(f"SUCCESS | Payment's (id={payment_id}) status was changed.", FILE_LOG)
#     return [update_response[0], payment_status]
# debug_log(f"FAILED | Payment's (id={payment_id}) status wasn't changed with comment: {update_response[1]}", FILE_LOG)
# return [update_response[1], payment_status]
