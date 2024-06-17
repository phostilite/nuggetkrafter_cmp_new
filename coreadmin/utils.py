from datetime import timedelta


def str_to_seconds(time_str):
    h, m, s = time_str.split(':')
    return timedelta(hours=int(h), minutes=int(m), seconds=float(s)).total_seconds()