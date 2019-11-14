# -*- coding: utf-8 -*-

import os
import re
from collections import namedtuple
import gzip
import sys
import json
import logging
from datetime import datetime
import argparse

logging.basicConfig(format = u'[%(asctime)s] %(levelname).1s %(message)s', filename="log_analyzer.log", level=logging.INFO, datefmt='%Y.%m.%d %H:%M:%S')

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

default_config = {
    "REPORT_SIZE": 1,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}

def now():
    return str(datetime.now())

def get_external_config():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--config', help='CMD')
    args = parser.parse_args()
    config = default_config
    external_config = args.config
    if external_config is not None:
        if os.path.exists(external_config):
            try:
                with open(external_config, 'r') as conf:
                    external_settings = json.load(conf)
                config["REPORT_SIZE"] = external_settings["REPORT_SIZE"]
                config["REPORT_DIR"] = external_settings["REPORT_DIR"]
                config["LOG_DIR"] = external_settings["LOG_DIR"]
                logging.info("use external config")
            except:
                logging.info("could not parse config")
                return "1"
        else:
            logging.info("config file is not wxists")
            return "2"
    logging.info(f"result config is {config}")
    return config

def get_last_log(logdir):
    files = os.listdir(logdir)
    if files:
        last = ""
        for file in files:
            m = re.match('^nginx-access-ui.log-\d{8}($|.gz$)', file)
            if m is not None:
                if file > last:
                    last = file
                    date = file.split("-")[-1].split(".")[0]
                    path = str(os.path.abspath(logdir)) + "/" + last
                    extension = "gz" if last.split(".")[-1] == "gz" else ""
        logging.info(f"choised log file is {last}")
        logging.info("no log files matched")

        Lastlog = namedtuple('Lastlog', 'date path extension')
        my_log = Lastlog(date, path, extension)
        logging.info(f"pring {my_log} ")
        return my_log

def parse_line(strings):
    for string in strings:
        url = str(string).split('"')[1]
        time = str(string).split(" ")[-1].replace("\n","").replace("\\n'", "")
        yield url, time


def get_lines(file):
    if file.extension == "gz":
        log = gzip.open(file.path, 'r+')
    else:
        log = open(file.path, 'r+', encoding='utf-8')
    for line in log:
        yield(line)


def r2(number):
    return round(number, 3)


def get_statistics(parsedlines):
    d = dict()
    all_count = 0
    all_time = 0.0
    err_count = 0
    for parsedline in parsedlines:
        all_count += 1
        try:
            all_time += r2(float(parsedline[1]))
            if d.get(parsedline[0]) is None:
                time_pack = []
                direct_count = 1
                time_pack.append(r2(float(parsedline[1])))
                d.update({parsedline[0]: [direct_count, r2(float(parsedline[1])), r2(float(parsedline[1])),
                                          r2(float(parsedline[1])), all_count, time_pack]})
            else:
                payload = d.get(parsedline[0])
                direct_count = payload[0] + 1
                time_sum = r2(float(payload[3]) + float(parsedline[1]))
                time_avg = r2(time_sum/direct_count)
                time_pack = payload[5]
                time_pack.append(r2(float(parsedline[1])))
                if payload[2] > r2(float(parsedline[1])):
                    time_max = r2(float(payload[2]))
                else:
                    time_max = r2(float(parsedline[1]))
                newpayload = [direct_count, time_avg, time_max, time_sum, all_count, time_pack]
                d[parsedline[0]] = newpayload
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

def handle_dict(d, all_time, report_size=default_config["REPORT_SIZE"], error_count = 0, error_percent = 21):
    res = []
    other = []
    all_count = len(d)
    if error_count/all_count * 100 >= error_percent:
        print( str(error_count/all_count * 100) + "more thae trashhole error percent " + str(error_percent) )
        return 1
    print("error percent is " + str(error_count/all_count * 100))
    for i in d.keys():
        pay = d[i]
        direct_count = pay[0]
        count_perc = r2(direct_count / all_count * 100)
        time_row = pay.pop()
        pay.pop()
        time_med = r2(mediana(time_row))
        time_perc = r2(pay[3]/all_time * 100)
        pay.append(count_perc)
        pay.append(time_med)
        pay.append(time_perc)
        d[i] = pay
    for i, j in d.items():
        if j[3] < float(report_size):
            continue
        else:
            res.append( [i, *j])
    h = sorted(res, key=lambda x: x[3], reverse = True)
    for k in h:
        other.append( {"count" : k[1], "count_perc": k[5], "time_avg": k[3], "time_max":k[4], "time_med": k[6], "time_perc": k[7],
                       "time_sum": k[4], "url": k[0]  }  )
    return other


def main():
    try:
        logging.info("script started at " + now())
        config = get_external_config()

        if len(config) == 1:
            print("Wrong config")
            sys.exit(1)
        print(config)

        my_log = get_last_log(config["LOG_DIR"])
        if my_log is None:
            print("log not exists")
            sys.exit(1)
        else:
            print("correct log file found")
        reportname = "report" + my_log.date + ".html"
        reportfile = str(os.path.abspath(config["REPORT_DIR"])) + "/"  + reportname
        logging.info(f"reportfile is {reportfile}")

        if os.path.exists(reportfile):
            print("Report alredy created")
            sys.exit(1)
        else:
            lines = get_lines(my_log)
            print(lines)
            parsed = parse_line(lines)

            dicted = get_statistics(parsed)

            for dic in dicted:
                print(dic)
#                pass

            d1 = handle_dict(dic[0], dic[1], config["REPORT_SIZE"], dic[2])
            if d1 == 1:
                print("error percentage thrashhold occured")
                sys.exit(1)
            else:
                with open("report.html", "r") as report:
                    data = report.read()

                data = data.replace("$table_json", str(d1))

                with open(reportfile, "w") as report:
                    report.write(data)

        logging.info("script done at " + now())
    except:
        logging.exception("fatal message")

if __name__ == "__main__":
    main()
