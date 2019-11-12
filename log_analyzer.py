# -*- coding: utf-8 -*-

import os
import re
from collections import namedtuple, OrderedDict
import gzip
import sys
import json
import logging

logging.basicConfig(filename="log_analyzer.log", level=logging.INFO)

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    "REPORT_SIZE": 1,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


def get_external_config():
    external_config = sys.argv[1]
    if external_config:
        if os.path.exists(external_config):
            with open(external_config, 'r') as conf:
                external_settings = json.load(conf)
            config["REPORT_SIZE"] = external_settings["REPORT_SIZE"]
            config["REPORT_DIR"] = external_settings["REPORT_DIR"]
            config["LOG_DIR"] = external_settings["LOG_DIR"]
            logging.info("use external config")
        else:
            logging.info("use default config")
        logging.info(f"resule config is {config}")
    return config

def get_last_log(logdir):
    files = os.listdir(logdir)
#    files = os.listdir(config["LOG_DIR"])
    last = ""
    for file in files:
        m = re.match('^nginx-access-ui.log-\d{8}($|.gz$)', file)
        if m is not None:
            if file > last:
                last = file
                date = file.split("-")[-1].split(".")[0]
                path = str(os.path.abspath(config["LOG_DIR"])) + "/"  + last
                extension = "gz" if last.split(".")[-1] == "gz" else ""
    logging.info(f"choised log file is {last}")
    logging.info("no log files matched")

    Lastlog = namedtuple('Lastlog', 'date path extension')
    my_log = Lastlog(date, path, extension)
    logging.info(f"pring {my_log} ")
    return my_log

#print(*my_log)

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
    count_perc = 0.0
    time_perc = 0.0
    time_avg = 0.0
    time_max = 0.0
    time_med = 0.0
    for parsedline in parsedlines:

        all_count += 1
        all_time += r2(float(parsedline[1]))
        if d.get(parsedline[0]) is None:
            time_pack = []
            direct_count = 1
            time_pack.append(r2(float(parsedline[1])))
                                       #count              #time_avg            #time_max
            d.update({parsedline[0]: [direct_count, r2(float(parsedline[1])), r2(float(parsedline[1])),
                                     #time_sum
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
    yield d, all_time


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

def handle_dict(d, all_time):
    res = []
    other = []
#    replacement = {direct_count, time_avg, time_max, time_sum, all_count, url}
    all_count = len(d)
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
        if j[3] < float(config["REPORT_SIZE"]):
            continue
        else:
            res.append( [i, *j])
    h = sorted(res, key=lambda x: x[3], reverse = True)
    for k in h:
        other.append( {"count" : k[1], "count_perc": k[5], "time_avg": k[3], "time_max":k[4], "time_med": k[6], "time_perc": k[7],
                       "time_sum": k[4], "url": k[0]  }  )
    return other


def main():
    logging.info("script started at")
    config = get_external_config()

    my_log = get_last_log(config["LOG_DIR"])
    reportname = "report" + my_log.date + ".html"
    reportfile = str(os.path.abspath(config["REPORT_DIR"])) + "/"  + reportname
    logging.info(f"reportfile is {reportfile}")

    if os.path.exists(reportfile):
        print("Report alredy created")
        sys.exit(1)
    else:
        lines = get_lines(my_log)
        parsed = parse_line(lines)
        dicted = get_statistics(parsed)

        for dic in dicted:
            print(dic)
#            pass
        all_time = dic[1]
        d1 = handle_dict(dic[0], dic[1])

        with open("report.html", "r") as report:
            data = report.read()

        data = data.replace("$table_json", str(d1))

        with open(reportfile, "w") as report:
            report.write(data)

    logging.info("script done at")

if __name__ == "__main__":
    main()
