#!/usr/bin/env python3
"""
filtered_logger module
"""
import logging
import mysql.connector
import os
import re
from typing import List


PII_FIELDS = ("name", "email", "phone", "ssn", "password")


def main():
    """Logs the information about user records in a table"""
    fields = "name,email,phone,ssn,password,ip,last_login,user_agent"
    cols = fields.split(',')
    query = "SELECT {} FROM users;".format(fields)
    info_logger = get_logger()
    con = get_db()
    with con.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            record = map(
                lambda x: '{}={}'.format(x[0], x[1]),
                zip(cols, row),
            )
            message = '{};'.format('; '.join(list(record)))
            args = ("user_data", logging.INFO, None, None, message, None, None)
            log_records = logging.LogRecord(*args)
            info_logger.handle(log_records)


def get_db() -> mysql.connector.connection.MySQLConnection:
    """Creates a connection to a database"""
    host = os.getenv("PERSONAL_DATA_DB_HOST", "localhost")
    name = os.getenv("PERSONAL_DATA_DB_NAME", "")
    user = os.getenv("PERSONAL_DATA_DB_USERNAME", "root")
    pwd = os.getenv("PERSONAL_DATA_DB_PASSWORD", "")
    con = mysql.connector.connect(
        host=host,
        port=3306,
        user=user,
        password=pwd,
        database=name,
    )
    return con


def get_logger() -> logging.Logger:
    """Creates new logger for user data"""
    logger = logging.getLogger("user_data")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(RedactingFormatter(PII_FIELDS))
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.addHandler(stream_handler)
    return logger


def filter_datum(fields: List[str], redaction: str,
                 message: str, separator: str) -> str:
    """Returns obfuscated log message"""
    return re.sub(r'(?P<field>{})=[^{}]*'.format('|'.join(fields), separator),
                  r'\g<field>={}'.format(redaction), message)


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
        """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """Formats a LogRecord"""
        msg = super(RedactingFormatter, self).format(record)
        text = filter_datum(self.fields, self.REDACTION, msg, self.SEPARATOR)
        return text


if __name__ == "__main__":
    main()
