import settings, logger, db
import hashlib, uuid, hmac
import requests


def generate_headers(request_body, request_method, request_url):
    """ CREATE headers for request """

    request_id = uuid.uuid4().hex
    x_site_id = settings.PAYSELECTION_SITE_ID
    site_secret_key = settings.PAYSELECTION_PRIVATE_KEY
    signature_string = f"{request_method}\n{request_url}\n{x_site_id}\n{request_id}\n{request_body}"

    signature_string = hmac.new(
        key=site_secret_key.encode(),
        msg=signature_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    return {
        'Content-Type': 'application/json',
        'X-SITE-ID': settings.PAYSELECTION_SITE_ID,
        'X-REQUEST-ID': request_id,
        'X-REQUEST-SIGNATURE': signature_string,
    }


def send_request(session, request_method: str, url: str, request_url: str,  request_body='{}'):
    """ SEND REQUEST """

    req = requests.Request(
        request_method,
        url,
        data=request_body,
        headers=generate_headers(request_body, request_method, request_url)
    )

    prepare_request = req.prepare()

    try:
        response = session.send(prepare_request)
    except requests.exceptions.ConnectTimeout:
        return None

    if response.ok:
        return response
    return None


def order_request(session, order_id):
    request_url = f"/orders/{order_id}"
    url = f"{settings.GW_API_URL}{request_url}"
    return send_request(session, 'GET', url, request_url)


def transaction_request(session, transaction_id):
    request_url = f"/transactions/{transaction_id}"
    url = f"{settings.GW_API_URL}{request_url}"
    return send_request(session, 'GET', url, request_url)


class PaySelection:
    STATUSES = {
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
    def status(order_id: str) -> str:
        session = requests.Session()

        order = order_request(session, order_id)
        if not order:
            return None

        order_json = order.json()
        transaction_id = order_json[0].get('TransactionId', None)
        if not transaction_id:
            return None

        transaction = transaction_request(session, transaction_id)
        if not transaction:
            return None

        transaction_json = transaction.json()
        transaction_state = transaction_json.get("TransactionState", None)
        if not transaction_state:
            return None

        payment_state = PaySelection.operation_statuses.get(transaction_state, None)
        if not payment_state:
            return None
        return payment_state

    # @staticmethod
    # def check_payment_status(order_id):
    #     order_response = make_order_request(s, order_id)
    #     if order_response is None:
    #         return None
    #
    #     order_json = order_response.json()
    #     transaction_id = order_json[0]['TransactionId']
    #
    #     transaction_response = make_transaction_request(s, transaction_id)
    #     if transaction_response is None:
    #         return None
    #
    #     transaction_json = transaction_response.json()
    #     transaction_state = transaction_json.get("TransactionState", None)
    #
    #     if transaction_state is None:
    #         debug_log(
    #             f"PaySelection | ERROR | Error: TransactionState is None",
    #             FILE_LOG
    #         )
    #         return None
    #
    #     payment_state = PaySelection.operation_statuses.get(
    #         transaction_state, None)
    #     if payment_state is None:
    #         debug_log(
    #             f"PaySelection | ERROR | Error: unknown transaction state {transaction_state}",
    #             FILE_LOG
    #         )
    #
    #     return payment_state

    @staticmethod
    def update_status(payment: dict) -> list:

        transaction_id = payment.get('transaction_id', None)
        # transaction_id = payment.get('transaction', None)
        payment_id = payment.get('payment_id', None)
        logger.logging(text=f"PAYSELECTION payment(#{payment_id}) with transaction: {transaction_id}", log_type="info")

        if payment_id and transaction_id:
            try:
                transaction_status = PaySelection.status(transaction_id)

                #     new_state = PaySelection.check_payment_status(transaction_id)
                #     return PaySelection.payment_update(payment_id, new_state, payment_dict['state'])
            except Exception as error:
                logger.logging(text=f"Payment(#{payment_id}) error: {error}\n", log_type="error")
        else:
            logger.logging(text=f"Payment hasn't payment_id or transaction_id: {payment}\n", log_type="error")
        return [False, None]



# from .payments_keys import PAYSELECTION_SITE_ID, PAYSELECTION_PRIVATE_KEY
# from settings.debug_log import debug_log
# from settings.db import try_except_callproc_request_to_db
#
#
# class PaySelection:
#     @staticmethod
#     def payment_update(payment_id, new_state, current_state):
#         if new_state is not None and new_state != current_state:
#             selector_list = [payment_id, new_state,
#                              f"Смена статуса: {current_state} -> {new_state}", SERVICE_ID, 'ru']
#             update_response = try_except_callproc_request_to_db(
#                 'payment_update', selector_list, 'PaySelection.payment_update')
#             debug_log(
#                 f"SUCCESS | Changing DB response is {update_response}", FILE_LOG)
#
#             if update_response[0]:
#                 debug_log(
#                     f"SUCCESS | Payment's (id={payment_id}) status was changed.", FILE_LOG)
#                 return [update_response[0], new_state]
#             debug_log(
#                 f"FAILED | Payment's (id={payment_id}) status wasn't changed with comment: {update_response[1]}", FILE_LOG)
#
#             return [update_response[1], new_state]
#
#         return [False, None]


