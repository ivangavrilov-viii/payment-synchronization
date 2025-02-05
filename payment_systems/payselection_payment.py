import uuid
from .payments_keys import PAYSELECTION_SITE_ID, PAYSELECTION_PRIVATE_KEY
from settings.debug_log import debug_log
import requests
import hashlib
import hmac
from settings.db import try_except_callproc_request_to_db

SERVICE_ID = 22809
FILE_LOG = "payselection_payment.txt"
GW_API_URL = 'https://gw.payselection.com'


def to_fixed(number_object, digits=0):
    """ Функция для форматирования суммы в строку с двумя знаками после запятой """

    return f"{number_object:.{digits}f}"


def signature_string(request_method, request_body, request_url, request_id):
    # Задайте параметры запроса
    x_site_id = PAYSELECTION_SITE_ID

    # Задайте ваш секретный ключ или публичный ключ (тест)
    site_secret_key = PAYSELECTION_PRIVATE_KEY

    # Создайте строку для вычисления сигнатуры
    signature_string = f"{request_method}\n{request_url}\n{x_site_id}\n{request_id}\n{request_body}"

    # Вычислите сигнатуру запроса
    signature = hmac.new(
        key=site_secret_key.encode(),
        msg=signature_string.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()

    # Теперь signature содержит сгенерированную сигнатуру
    return signature


def generate_headers(request_body, request_method, request_url):
    request_id = uuid.uuid4().hex

    return {
        'Content-Type': 'application/json',

        'X-SITE-ID': PAYSELECTION_SITE_ID,
        'X-REQUEST-ID': request_id,
        'X-REQUEST-SIGNATURE': signature_string(request_method, request_body, request_url, request_id),
    }


def send_request(session, request_method, url, request_url,  request_body='{}'):

    req = requests.Request(
        request_method,
        url,
        data=request_body,
        headers=generate_headers(request_body, request_method, request_url))

    prep_req = req.prepare()

    response = None
    try:
        response = session.send(prep_req)
    except requests.exceptions.ConnectTimeout:
        debug_log(
            f"{url} | ERROR | Operation timeout",
            FILE_LOG
        )
        return None

    # print(prep_req.method + ' ' + prep_req.url)
    # for key, value in prep_req.headers.items():
    #     print(f"{key}: {value}")
    # print(prep_req.body)
    # print(response.status_code, response.text)

    if response.ok:
        debug_log(
            f"PaySelection {url} | SUCCESS | Code: {response.status_code} Body: {response.text}",
            FILE_LOG
        )
        return response
    else:
        debug_log(
            f"PaySelection {url} | ERROR | Error: {response.status_code} Body: {response.text}",
            FILE_LOG
        )
        return None


def make_order_request(session, order_id):
    request_url = f"/orders/{order_id}"
    url = f"{GW_API_URL}{request_url}"
    return send_request(session, 'GET', url, request_url)


def make_transaction_request(session, transaction_id):
    request_url = f"/transactions/{transaction_id}"
    url = f"{GW_API_URL}{request_url}"
    return send_request(session, 'GET', url, request_url)


def payment_to_refund_data(payment_data, transaction_id):
    return {
        'TransactionId': transaction_id,
        'Amount': to_fixed(payment_data['amount'], 2),
        # 'Currency': payment_data['currency']
        'Currency': 'RUB'
    }


def make_refund_request(session, refund_data):
    request_url = f"/payments/refund"
    url = f"{GW_API_URL}{request_url}"
    return send_request(session, 'POST', url, request_url, refund_data)


class PaySelection:
    operation_statuses = {
        'success': 'succeeded',
        'voided': 'canceled',
        'preauthorized': 'pending',
        'pending': 'pending',
        'declined': 'rejected',
        'wait_for_3ds': '3ds-checking',
        'redirect': '3ds-checked',
        'submitted': 'pending',
        'new': 'new'
    }

    @staticmethod
    def check_payment_status(order_id):
        s = requests.Session()
        if order_id is None:
            # print(
            #     f"PaySelection | ERROR | Error: order_id is None"
            # )
            debug_log(
                f"PaySelection | ERROR | Error: order_id is None",
                FILE_LOG
            )
            return None

        order_response = make_order_request(s, order_id)
        if order_response is None:
            return None

        order_json = order_response.json()
        transaction_id = order_json[0]['TransactionId']

        transaction_response = make_transaction_request(s, transaction_id)
        if transaction_response is None:
            return None

        transaction_json = transaction_response.json()
        transaction_state = transaction_json.get("TransactionState", None)

        if transaction_state is None:
            debug_log(
                f"PaySelection | ERROR | Error: TransactionState is None",
                FILE_LOG
            )
            return None

        payment_state = PaySelection.operation_statuses.get(
            transaction_state, None)
        if payment_state is None:
            debug_log(
                f"PaySelection | ERROR | Error: unknown transaction state {transaction_state}",
                FILE_LOG
            )

        return payment_state

    @staticmethod
    def payment_update(payment_id, new_state, current_state):
        if new_state is not None and new_state != current_state:
            selector_list = [payment_id, new_state,
                             f"Смена статуса: {current_state} -> {new_state}", SERVICE_ID, 'ru']
            update_response = try_except_callproc_request_to_db(
                'payment_update', selector_list, 'PaySelection.payment_update')
            debug_log(
                f"SUCCESS | Changing DB response is {update_response}", FILE_LOG)

            if update_response[0]:
                debug_log(
                    f"SUCCESS | Payment's (id={payment_id}) status was changed.", FILE_LOG)
                return [update_response[0], new_state]
            debug_log(
                f"FAILED | Payment's (id={payment_id}) status wasn't changed with comment: {update_response[1]}", FILE_LOG)

            return [update_response[1], new_state]

        return [False, None]

    @staticmethod
    def update_payment_status(payment_dict: dict) -> list:
        try:
            transaction_id = payment_dict['transaction']
            payment_id = payment_dict['payment_id']
            current_state = payment_dict['state']

            debug_log(
                f"PaySelection | INFO | update_payment_status #{payment_id} {transaction_id}",
                FILE_LOG
            )

            if transaction_id is None:
                return [False, None]

            new_state = PaySelection.check_payment_status(transaction_id)
            return PaySelection.payment_update(payment_id, new_state, current_state)
        except Exception as error:
            debug_log(
                f"ERROR. Error with payment (id={payment_id}) to change status: {error}", FILE_LOG)
            return [False, None]
