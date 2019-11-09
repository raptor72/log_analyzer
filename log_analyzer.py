# -*- coding: utf-8 -*-

import os
import re
from collections import namedtuple, OrderedDict
import gzip

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}

files = os.listdir(config["LOG_DIR"])
last = ""
for file in files:
     m = re.match('^nginx-access-ui.log-\d{8}($|.gz$)', file)
     if m is not None:
         if file > last:
             last = file
             date = file.split("-")[-1].split(".")[0]
             path = str(os.path.abspath(config["LOG_DIR"])) + "/"  + last
             extension = "gz" if last.split(".")[-1] == "gz" else ""



Lastlog = namedtuple('Lastlog', 'date path extension')
my_log = Lastlog(date, path, extension)

print(*my_log)

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
    return round(number, 2)


def get_statistics(parsedlines):
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
            d.update({parsedline[0]: [direct_count, r2(direct_count/all_count), r2(all_time/all_count), r2(float(parsedline[1])),
                                      time_med, r2(float(parsedline[1])/all_time), r2(float(parsedline[1])), all_count, time_pack]})
        else:
            payload = d.get(parsedline[0])
            direct_count = payload[0] + 1
            count_perc = r2(direct_count/all_count)
            time_sum = r2(float(payload[2]) + float(parsedline[1]))
            time_perc = r2(time_sum/all_time)
            time_avg = r2(time_sum/direct_count)
            time_pack = payload[8]
            time_pack.append(r2(float(parsedline[1])))
            if payload[5] > r2(float(parsedline[1])):
                time_max = r2(float(payload[5]))
            else:
                time_max = r2(float(parsedline[1]))
            newpayload = [direct_count, count_perc, time_avg, time_max, time_med, time_perc, time_sum, all_count, time_pack]
            d[parsedline[0]] = newpayload
    yield d


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

def handle_dict(d):
    res = []

    def keyFunk(item):
        return item[6]

    all_count = len(d)
    for i in d.keys():
        pay = d[i]
        direct_count = pay[0]
        count_perc = r2(direct_count / all_count)
        time_row = pay.pop()
        time_med = r2(mediana(time_row))
        pay[1] = count_perc
        pay[6] = time_med
        d[i] = pay

#    for i, j in d.items():
#        res.append([i, *j])

#    return res.sort(key=keyFunk)
    return d

lines = get_lines(my_log)
parsed = parse_line(lines)
dicted = get_statistics(parsed)



d = dict()

for dic in dicted:
    print(dic)
#    pass
print(len(dic))


d1 = handle_dict(dic)

with open("report.txt", "w") as report:
    for i in d1:
        report.write(i + " " + str(d1[i]) + '\n')


def main():
    pass

if __name__ == "__main__":
    main()
