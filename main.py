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
