import zipfile
import sys
import re
import datetime

from collections import Counter

# PATTERN = re.compile('(^.* - - )\[(.*)\+[0-9].+\] \"(.*) (\/.*)(\?.*)\" ([0-9]{3})')
# PATTERN = re.compile('(^.* - - )\[(.*)\+[0-9].+\] \"(.*) (\/.*)\.*" ([0-9]{3})')
# PATTERN = re.compile('(^.* - - )\[(.*)\+[0-9].+\] \"(.*) (\/.*)\ (HTTP.*)" ([0-9]{3})')
PATTERN = re.compile('(^.* - - )\[(.*)\+[0-9].+\] \"([A-Z]+) (.*)\.*" ([0-9]{3})')


class Bcolors(object):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[0;32m'
    ENDC = '\033[0m'


def log_string_to_request_class(data_string, pattern):
    """
    convert and parse each log record
    :param data_string:
    :param pattern:
    :return:
    """
    result = pattern.search(data_string)
    date = result.group(2)
    req_type = result.group(3)
    # req_url = re.sub(r"/\?.*/", '', result.group(4))
    req_url = result.group(4).split('?')[0].split(' ')[0]
    req_status = result.group(5)
    return RequestClass(date, req_type, req_url, req_status)


def read_from_file_to_request_class_list(file_name):
    """
    read from log file and convert each line to request class object
    :param file_name:
    :return:
    """
    obj_list = []
    with zipfile.ZipFile(file_name) as z:
        with z.open('access_log') as f:
            for log_string in f:
                obj_list.append(log_string_to_request_class(log_string, PATTERN))
    return obj_list


def get_duration(start_time, end_time, units=None):
    duration = (end_time - start_time).total_seconds()
    if units == 'minutes':
        duration = (end_time - start_time).total_seconds()/60
    if units == 'hours':
        duration = (end_time - start_time).total_seconds() / 3600
    return duration


def count_tpm(transaction_amount, duration):
    return transaction_amount / duration


def top_n_transactions_statistics(top_amount, logs_list, total_transactions_amount, duration_time):
    result = []
    counter = Counter()
    for url in logs_list:
        counter[url.req_url] += 1

    for item in counter.most_common(top_amount):
        tmp_result = [
            item[1],
            float(item[1]) / total_transactions_amount * 100,
            count_tpm(int(item[1]), duration_time),
            item[0]
            ]
        result.append(tmp_result)
    return result


class RequestClass(object):

    def __init__(self, date_string, req_type, req_url, req_status):
        self.date = self.date_from_string(date_string)
        self.req_type = req_type
        self.req_url = req_url
        self.req_status = req_status

    @staticmethod
    def date_from_string(date_string):
        """
        convert date string to datetime object
        :param date_string:
        :return:
        """
        return datetime.datetime.strptime(date_string.rstrip(), '%d/%b/%Y:%H:%M:%S')


def main(file_name):

    payload = read_from_file_to_request_class_list(file_name)
    # sort log by date to ensure correct start and end time
    sorted(payload, key=lambda req_dict: req_dict.date)
    duration = get_duration(payload[0].date, payload[-1].date, 'minutes')
    total_transactions = len(payload)
    max_tpm = count_tpm(total_transactions, duration)
    transaction_stats = top_n_transactions_statistics(30, payload, total_transactions, duration)
    print(Bcolors.OKBLUE + 'total transactions {}'. format(total_transactions) + Bcolors.ENDC)
    print(Bcolors.OKBLUE + 'total duration in minutes {}'. format(duration) + Bcolors.ENDC)
    print(Bcolors.OKBLUE + 'max_tpm_all_transactions = {} \n'.format(max_tpm) + Bcolors.ENDC)
    for item in transaction_stats:
        print(Bcolors.OKGREEN + 'total hits: ' + Bcolors.ENDC + str(item[0]))
        print(Bcolors.OKGREEN + 'percentage: ' + Bcolors.ENDC + str(item[1]))
        print(Bcolors.OKGREEN + 'max_tpm: ' + Bcolors.ENDC + str(item[2]))
        print(Bcolors.OKGREEN + 'url: ' + Bcolors.ENDC + str(item[3]))


if __name__ == "__main__":
    main(sys.argv[1])
