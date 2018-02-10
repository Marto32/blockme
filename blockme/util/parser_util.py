import datetime


def convert_base_16_unix_time_to_datetime(base_16_string):
    """
    A helper function to convert a timestamp string in the
    format such as "0x56bfb41a" to a python datetime.datetime
    in UTC.
    """
    if not isinstance(base_16_string, str):
        raise Exception('`base_16_string` is expected to be a string '
            'such as "0x56bfb41a"')
    unixtime = int(base_16_string, 16)
    return datetime.datetime.utcfromtimestamp(unixtime)
