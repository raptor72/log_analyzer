# -*- coding: utf-8 -*-

import os
import re
from collections import namedtuple
import gzip
import sys
import json
import logging
import argparse

Lastlog = namedtuple('Lastlog', 'date path extension')

logging.basicConfig(format = u'[%(asctime)s] %(levelname).1s %(message)s', filename="log_analyzer.log", datefmt='%Y.%m.%d %H:%M:%S',
                    level=logging.INFO
                    )

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';


default_config = {
    "REPORT_SIZE": 25,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "ERROR_PERCENT" : 25,
}


def get_external_config():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='CMD')
    args = parser.parse_args()
    config = default_config
    external_config = args.config
    if external_config is not None:
        if os.path.exists(external_config):
            try:
                with open(external_config, 'r') as conf:
                    external_settings = json.load(conf)
                for i in external_settings.keys():
                    if config.get(i) is not None:
                        config[i] = external_settings[i]
                logging.info("use external config")
            except:
                logging.debug("could not parse config")
                return None
        else:
            logging.debug("config file is not exists")
            return None
    logging.info(f"result config is {config}")
    return config


def get_last_log(logdir):
    if os.listdir(logdir):
        last = ""
        pattern = re.compile('^nginx-access-ui.log-\d{8}($|.gz$)')
        for file in os.listdir(logdir):
            m = pattern.findall(file)
            if m is not None:
                if file > last:
                    last = file
                    date = file.split("-")[-1].split(".")[0]
                    path = os.path.join( os.path.abspath(logdir), last)
                    extension = "gz" if last.split(".")[-1] == "gz" else ""
            else:
                logging.debug("no log files matched")
        logging.info(f"choised log file is {last}")
        my_log = Lastlog(date, path, extension)
        return my_log
    else:
        logging.info("no logs found")


def parse_line(strings):
    for line in strings:
        url = line.split('"')[1]
        time = line.split(" ")[-1].replace("\n","").replace("\\n'", "")
        yield url, time


def get_lines(file):
    if file.extension == "gz":
        log = gzip.open(file.path, 'r+')
    else:
        log = open(file.path, 'r+', encoding='utf-8')
    for line in log:
        yield str(line)


def r2(number):
    return round(number, 3)


def get_statistics(parsed_lines):
    d = {}
    all_count = 0
    all_time = 0.0
    err_count = 0
    for url, strtime in parsed_lines:
        all_count += 1
        try:
            time = r2(float(strtime))
            all_time += time
            if d.get(url) is None:
                time_pack = []
                direct_count = 1
                time_pack.append(time)
                d.update({ url: [direct_count, time, time,
                        time, all_count, time_pack]})
            else:
                payload = d.get(url)
                direct_count = payload[0] + 1
                time_sum = r2(float(payload[3]) + time)
                time_avg = r2(time_sum / direct_count)
                time_pack = payload[5]
                time_pack.append(time)
                if payload[2] > time:
                    time_max = r2(float(payload[2]))
                else:
                    time_max = time
                updated_payload = [direct_count, time_avg, time_max, time_sum, all_count, time_pack]
                d[url] = updated_payload
        except:
            err_count +=1
    yield d, all_time, err_count


def mediana(data):
    smass = sorted(data)
    if len(data) % 2 == 0:
        mid1 = (int(len(sorted(data)) / 2))
        mid2 = (int(len(sorted(data)) / 2) - 1)
        result = (smass[mid1] + smass[mid2]) / 2
    else:
        mid = (int(len(sorted(data)) / 2))
        result = smass[mid]
    return result


def handle_dict(d, all_time, report_size=default_config["REPORT_SIZE"], error_count = 0, error_percent = 0):
    res = []
    sorted_list = []
    all_count = len(d)
    if error_count / all_count * 100 > error_percent:
        logging.info(f"Reach error threshold {str(error_count / all_count * 100)}")
        return 1
    for i in d.keys():
        pay = d[i]
        direct_count = pay[0]
        count_perc = r2(direct_count / all_count * 100)
        time_row = pay.pop()
        pay.pop()
        time_med = r2(mediana(time_row))
        time_perc = r2(pay[3] / all_time * 100)
        pay.append(count_perc)
        pay.append(time_med)
        pay.append(time_perc)
        d[i] = pay
    for i, j in d.items():
        if j[3] < float(report_size): #time_sum
            continue
        else:
            res.append( [i, *j])
    mediator = sorted(res, key=lambda x: x[3], reverse = True)
    for k in mediator:
        sorted_list.append({"count" : k[1], "count_perc": k[5], "time_avg": k[3], "time_max":k[4], "time_med": k[6], "time_perc": k[7],
                       "time_sum": k[4], "url": k[0]})
    return sorted_list


def main():
    logging.info("script started")
    config = get_external_config()
    if config is None:
        print("Wrong config")
        logging.error(f"Used wrond configuration file")
        sys.exit(1)

    my_log = get_last_log(config["LOG_DIR"])
    if my_log is None:
        print("no logs found")
        sys.exit(0)
    reportname = (f"report{my_log.date}.html")
    reportfile = os.path.join(os.path.abspath(config["REPORT_DIR"]), reportname)
    logging.info(f"reportfile is {reportfile}")

    if os.path.exists(reportfile):
        logging.info("Report alredy created")
        sys.exit(1)

    try:
        lines = get_lines(my_log)
        parsed = parse_line(lines)
        dicted = get_statistics(parsed)

        for dic in dicted:
            print(dic)

        d1 = handle_dict(dic[0], dic[1], config["REPORT_SIZE"], dic[2], config["ERROR_PERCENT"])
        if d1 == 1:
            print("error percentage treshhold occured")
            sys.exit(1)
        else:
            with open("report.html", "r") as report:
                data = report.read()

            data = data.replace("$table_json", str(d1))

            with open(reportfile, "w") as report:
                report.write(data)

        logging.info("script done")
    except:
        logging.exception("fatal unexpected error")

if __name__ == "__main__":
    main()
