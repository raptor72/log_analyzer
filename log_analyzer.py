# -*- coding: utf-8 -*-

import os
import re
from collections import namedtuple, defaultdict
import gzip
import sys
import json
import logging
import argparse
import datetime
import statistics

Lastlog = namedtuple('Lastlog', 'date path extension')

DEFAULT_CONFIG = './default_config'


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';


def load_config(config_path):
    with open(config_path, 'rb') as conf:
        config = json.load(conf, encoding='utf8')
    return config


def configure_logging(log_filename):
    logging.basicConfig(format = u'[%(asctime)s] %(levelname).1s %(message)s', filename=log_filename, datefmt='%Y.%m.%d %H:%M:%S',
                    level=logging.INFO
                    )


def get_last_log(logdir):
    try:
        os.listdir(logdir)
    except FileNotFoundError:
        logging.info("Log directory does not exists")
        return
    if os.listdir(logdir) == []:
        logging.info("Directory is empty")
        return
    last_date = datetime.date(1970, 1, 1).strftime('%Y%m%d')
    pattern = re.compile('^nginx-access-ui.log-(\d{8})($|.gz$)')
    for file in os.listdir(logdir):
        matched = pattern.match(file)
        if matched:
            current_date = datetime.datetime.strptime(matched.groups()[0], '%Y%m%d').strftime('%Y%m%d')
            if current_date > last_date:
                last_file = file
                last_date = current_date
                path = os.path.join( os.path.abspath(logdir), last_file)
                extension = matched.groups()[1]
        else:
            logging.debug("no log files matched")
    logging.info(f"choised log file is {last_file}")
    my_log = Lastlog(last_date, path, extension)
    return my_log


def parse_line(strings):
    for line in strings:
        try:
            url = line.split('"')[1]
            time = line.split(" ")[-1].replace("\n","").replace("\\n'", "")
            yield url, time
        except:
            yield None, None

def reader(file):
    if file.extension == ".gz":
        return gzip.open(file.path, 'r+')
    else:
        return open(file.path, 'r+', encoding='utf-8')


def get_lines(reader):
    with reader as f:
        for line in f:
            yield str(line)


def r2(number):
    return round(number, 3)


def get_statistics(parsed_lines):
    accumulated_dict = defaultdict(list)
    all_count = 0
    all_time = 0.0
    err_count = 0
    for url, strtime in parsed_lines:
        all_count += 1
        try:
            time = float(strtime)
            all_time += time

            if accumulated_dict.get(url) is None:
                time_pack = [time]
                direct_count = 1
                accumulated_dict[url].append([direct_count, time, time, time, all_count, time_pack])
                accumulated_dict[url] = accumulated_dict[url][0]
            else:
                payload = accumulated_dict.get(url)
                direct_count = payload[0] + 1
                time_sum = float(payload[3]) + time
                time_avg = time_sum / direct_count
                time_pack = payload[5]
                time_pack.append(time)
                if payload[2] > time:
                    time_max = float(payload[2])
                else:
                    time_max = time
                updated_payload = [direct_count, time_avg, time_max, time_sum, all_count, time_pack]
                accumulated_dict[url] = updated_payload
        except:
            err_count += 1
    return accumulated_dict, all_time, err_count


def handle_dict(accumulated_dict, all_time, report_size, error_count = 0, error_percent = 0):
    res = []
    all_count = len(accumulated_dict)
    if error_count / all_count * 100 > error_percent:
        logging.info(f"Reach error threshold {str(error_count / all_count * 100)}")
        return 1
    for i in accumulated_dict.keys():
        pay = accumulated_dict[i]
        direct_count = pay[0]
        count_perc = direct_count / all_count * 100
        time_pack = pay.pop()
        time_med = statistics.median(time_pack)
        time_perc = pay[3] / all_time * 100
        accumulated_dict[i] = pay
        if pay[3] > float(report_size):
            res.append(
                {"count": direct_count,
                 "count_perc": r2(count_perc),
                 "time_avg": r2(pay[1]),
                 "time_max": r2(pay[2]),
                 "time_med": r2(time_med),
                 "time_perc": r2(time_perc),
                 "time_sum": r2(pay[3]),
                 "url": i}
            )
    return sorted(res, key=lambda x: x["time_avg"], reverse=True)


def render_report(reportfile, replacement):
    with open("report.html", "r") as report:
        data = report.read()
    data = data.replace("$table_json", str(replacement))
    with open(reportfile, "w") as report:
        report.write(data)


def main(config):
    logging.info("script started")
    if config is None:
        logging.error(f"Used wrong configuration file")
        sys.exit(1)
    logging.info(f"result config is: {config}")
    my_log = get_last_log(config["LOG_DIR"])
    if my_log is None:
        logging.info("no logs found")
        sys.exit(0)
    reportname = (f"report{my_log.date}.html")
    if not os.path.exists(config["REPORT_DIR"]):
        os.makedirs(config["REPORT_DIR"])
    reportfile = os.path.join(os.path.abspath(config["REPORT_DIR"]), reportname)
    logging.info(f"reportfile is {reportfile}")

    if os.path.exists(reportfile):
        logging.info("Report alredy created")
        return

    lines = get_lines(reader(my_log))
    parsed = parse_line(lines)
    collected_data = get_statistics(parsed)
    result_replacement = handle_dict(collected_data[0], collected_data[1], config["REPORT_SIZE"], collected_data[2], config["ERROR_PERCENT"])
    if result_replacement == 1:
        logging.info("error percentage threshold occurred")
        sys.exit(1)
    else:
        render_report(reportfile, result_replacement)
    logging.info("script done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='config path', default=DEFAULT_CONFIG)
    args = parser.parse_args()

    config = load_config(DEFAULT_CONFIG)
    if args.config:
        external_config = load_config(args.config)
        config.update(external_config)

    configure_logging(config["LOG_FILE"])

    try:
        main(config)
    except:
        logging.exception("fatal unexpected error")

