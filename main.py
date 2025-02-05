from payment_systems import yookassa
from payment_systems import tbank

import traceback
import settings
import logger

import sys
import db


if __name__ == "__main__":
    logger.logging(text="Start synchronization of payments", log_type='info')

    try:
        payments = db.get_data(db_function=settings.GET_PAYMENTS, selector_list=[settings.LANGUAGE])
        logger.logging(text=f"Payments(len: {len(payments)}): {payments}\n", log_type='info')

        for payment in payments:
            payment_id = payment.get('payment_id', None)
            source = payment.get('source', None)
            payment_status = None

            logger.logging(text=f"Source for payment(#{payment_id}) is {source}", log_type='info')

            if source == 'tinkoff-pay':
                payment_status = tbank.tbank_status(payment)
            elif source == 'yookassa':
                payment_status = yookassa.yookassa_status(payment)
            elif source == 'payselection':
                pass
            elif source:
                logger.logging(text=f"UNKNOWN SOURCE for payment", log_type='warning')
            else:
                logger.logging(text=f"Payment hasn't source", log_type='warning')
        logger.logging(text=f"Synchronization of payments is ENDED\n", log_type='success')
    except Exception as error:
        tb = traceback.format_exc()
        logger.logging(text=f"Synchronization of payments is FAILED. Error: {error}", log_type="critical")
        sys.exit(1)




# if payment['source'] == 'tinkoff-pay':
#     debug_log(f"INFO | This is tinkoff-pay payment", FILE_LOG)
#     payment_status = get_payment_status(payment)
#
#     if payment_status[0]:
#         debug_log(
#             f"INFO | Payment's (id={payment['payment_id']}) status was changed to {payment_status}", FILE_LOG)
#     else:
#         debug_log(
#             f"INFO | Payment status is {payment_status}", FILE_LOG)
# elif payment['source'] == 'yookassa':
#     debug_log(f"INFO | This is yookassa payment", FILE_LOG)
#     payment_status = get_yookassa_payment_status(payment)
#
#     if payment_status[0]:
#         debug_log(
#             f"INFO | Payment's (id={payment['payment_id']}) status was changed to {payment_status}", FILE_LOG)
#     else:
#         debug_log(
#             f"INFO | Payment status is {payment_status}", FILE_LOG)
# elif payment['source'] == 'payselection':
#     debug_log(f"INFO | This is payselection payment", FILE_LOG)
#     payment_status = PaySelection.update_payment_status(payment)
#     if payment_status[0]:
#         debug_log(
#             f"INFO | Payment's (id={payment['payment_id']}) status was changed to {payment_status}", FILE_LOG)
#     else:
#         debug_log(
#             f"INFO | Payment status is {payment_status}", FILE_LOG)
