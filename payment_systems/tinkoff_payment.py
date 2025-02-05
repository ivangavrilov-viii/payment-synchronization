from .payments_keys import TINKOFF_PASSWORD, TINKOFF_TERMINAL_KEY
from settings.db import try_except_callproc_request_to_db
from settings.debug_log import debug_log
import configparser
import requests
import hashlib
import json


def get_payment_status(payment_dict: dict) -> list:
    """ Get Tinkoff payment status. If the status differs from the status in the database, change it """

    FILE_LOG = "tinkoff_payment.txt"
    func_name = 'get_payment_status'
    transaction_id = payment_dict['transaction']
    payment_id = payment_dict['payment_id']
    service_id = 22809

    try:
        if transaction_id and payment_id:
            debug_log(f"INFO | Start get status of payment(id={payment_id})", FILE_LOG)

            Token_data = TINKOFF_PASSWORD + str(transaction_id) + TINKOFF_TERMINAL_KEY
            Token = hashlib.sha256(Token_data.encode('utf-8')).hexdigest()
            data = json.dumps({
                "TerminalKey": TINKOFF_TERMINAL_KEY,
                "PaymentId": int(transaction_id),
                "Token": Token
            }, separators=(',', ':'))

            response = requests.post('https://securepay.tinkoff.ru/v2/GetState', data=data, headers={"Content-Type": "application/json"})
            data_return = response.json()
            debug_log(f"SUCCESS | Get status of payment(id={payment_id}). Response = {data_return}", FILE_LOG)

            if data_return['Status']:
                payment_status = data_return['Status'].lower().replace('_', '-')
                debug_log(f"INFO | Status of payment(id={payment_id}) is {payment_status}", FILE_LOG)

                if payment_status != payment_dict['state']:
                    debug_log(f"INFO | Status of payment(id={payment_id}) is different. Was {payment_dict['state']}. Now {payment_status}", FILE_LOG)
                    selector_list = [payment_id, payment_status, f"Смена статуса: {payment_dict['state']} -> {payment_status}", service_id, 'ru']
                    update_response = try_except_callproc_request_to_db('payment_update', selector_list, func_name)
                    debug_log(f"SUCCESS | Changing DB response is {update_response}", FILE_LOG)

                    if update_response[0]:
                        debug_log(f"SUCCESS | Payment's (id={payment_id}) status was changed.", FILE_LOG)
                        return [update_response[0], payment_status]
                    debug_log(f"FAILED | Payment's (id={payment_id}) status wasn't changed with comment: {update_response[1]}", FILE_LOG)
                    return [update_response[1], payment_status]
        return [False, None]
    except Exception as error:
        debug_log(f"ERROR. Error with payment (id={payment_id}) to change status: {error}", FILE_LOG)
        return [False, None]
