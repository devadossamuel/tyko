import re
from datetime import datetime, date

DATE_FORMATS = {
    1: "%Y",
    2: "%m-%Y",
    3: "%m-%d-%Y",
}
DATE_PRECISIONS_REGEX = {
    1: re.compile(r'^([0-9]{4})$'),
    2: re.compile(r'^([0-1][0-9])-([0-9]{4})$'),
    3: re.compile(r'^([0-1][0-9])-([0-3][0-9])-([0-9]{4})$')
}


def identify_precision(data) -> int:
    for precision, matcher in DATE_PRECISIONS_REGEX.items():
        if matcher.match(data):
            return precision
    raise AttributeError("Unable to identify format for string {}".format(data))


def create_precision_datetime(date: str, precision: int = 3):

    formatter = DATE_FORMATS.get(precision)
    if formatter is None:
        raise AttributeError("Invalid precision type")
    return datetime.strptime(date, formatter)


def serialize_precision_datetime(date: date, precision=3) -> str:
    formatter = DATE_FORMATS.get(precision)
    if formatter is None:
        raise AttributeError("Invalid precision type")
    return date.strftime(formatter)
    # if precision == 3:
    #     return date.strftime("%m-%d-%Y")
    #
    # if precision == 2:
    #     return date.strftime("%m-%Y")
    #
    # if precision == 1:
    #     return date.strftime("%Y")