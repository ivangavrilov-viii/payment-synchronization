import logger
import settings
import psycopg2


def start_db_connection():
    return psycopg2.connect(
        database=settings.DB_NAME,
        user=settings.DB_USER,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        password=settings.DB_PASSWORD
    )


def stop_db_connection():
    CONNECTION.close()
    logger.logging(text=f"Connection with DataBase was closed", log_type="info")


def get_data(db_function, selector_list):
    """ Request to DB in "try-except" construction """

    try:
        response = make_callproc(db_function, selector_list)
        response = response[0][0] if response and response[0] else list()
        return response
    except Exception as error:
        logger.logging(text=f'Error with "{db_function}({selector_list})". Error: {error}', log_type='error')
        return list()


def db_request(db_function_name, selector_list):
    cursor = CONNECTION.cursor()
    cursor.callproc(db_function_name, selector_list)
    data = cursor.fetchall()
    CONNECTION.commit()
    return data


def make_callproc(db_function_name, selector_list):
    global CONNECTION

    try:
        return db_request(db_function_name, selector_list)
    except psycopg2.errors.ConnectionException as error:
        logger.logging(text=f'Error with "{cursor.query}". Error with connection: {error}', log_type='warning')
        stop_db_connection()

        while True:
            logger.logging(text=f'Start to reconnect to DataBase.', log_type='warning')

            try:
                CONNECTION = start_db_connection()
                return db_request(db_function_name, selector_list)
            except psycopg2.Error as error:
                logger.logging(text=f'Error with reconnect: {error}', log_type='critical')
    except psycopg2.DatabaseError as error:
        logger.logging(text=f'Error with "{cursor.query}". Error: {error}', log_type='warning')
        stop_db_connection()

        while True:
            logger.logging(text=f'Start to reconnect to DataBase.', log_type='warning')

            try:
                CONNECTION = start_db_connection()
                return db_request(db_function_name, selector_list)
            except Exception as error:
                logger.logging(text=f'Error with reconnect: {error}', log_type='critical')
                return None

CONNECTION = start_db_connection()
