from payment_systems.payselection import PaySelection
from payment_systems import yookassa, tbank
import traceback, sys, settings, logger, db


if __name__ == "__main__":
    logger.logging(text="Start synchronization of payments", log_type='info')

    try:
        selector_list = ['flatinn', None, None, '2025-01-01', '2025-12-01', settings.LANGUAGE]
        payments = db.get_data(db_function=settings.GET_PAYMENTS, selector_list=selector_list)
        # payments = db.get_data(db_function=settings.GET_PAYMENTS, selector_list=[settings.LANGUAGE])
        logger.logging(text=f"Payments(len: {len(payments)}): {payments}\n", log_type='info')

        for payment in payments:
            payment_id = payment.get('payment_id', None)
            source = payment.get('source', None)
            payment_status = None

            logger.logging(text=f"Source for payment(#{payment_id}) is {source}", log_type='info')

            if source == 'tinkoff-pay':
                payment_status = tbank.tbank_status(payment)
            elif source == 'yookassa':
                pass
                # payment_status = yookassa.yookassa_status(payment)
            elif source == 'payselection':
                pass
                # payment_status = PaySelection.update_status(payment)
            elif source:
                logger.logging(text=f"UNKNOWN SOURCE for payment", log_type='warning')
            else:
                logger.logging(text=f"Payment hasn't source", log_type='warning')
        logger.logging(text=f"Synchronization of payments is ENDED\n", log_type='success')
    except Exception as error:
        tb = traceback.format_exc()
        logger.logging(text=f"Synchronization of payments is FAILED. Error: {error}", log_type="critical")
        sys.exit(1)
