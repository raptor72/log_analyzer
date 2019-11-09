# -*- coding: utf-8 -*-

import os
import re
from collections import namedtuple
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
#             print(last)
             date = file.split("-")[-1].split(".")[0]
#             path = os.path.abspath(last)
             path = str(os.path.abspath(config["LOG_DIR"])) + "/"  + last
#             path = str(os.listdir(config["LOG_DIR"])) + last
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
#    open = open if file.extension == "" else gzip.open

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
        all_time += float(parsedline[1])
        if d.get(parsedline[0]) is None:

            direct_count = 1
#            d.update( {parsedline[0] : (parsedline[1], count)} )
                                       #count           #count_perc          #time_sum         #time_perc             #time_avg          time_max
            d.update({parsedline[0]: (direct_count, r2(direct_count/all_count), r2(float(parsedline[1])), r2(float(parsedline[1])/all_time),
                                      r2(all_time/all_count), r2(float(parsedline[1])), time_med,  all_count)})
        else:
            payload = d.get(parsedline[0])
            direct_count = payload[0] + 1
            count_perc = r2(direct_count/all_count)
            time_sum = r2(float(payload[2]) + float(parsedline[1]))
            time_perc = r2(time_sum/all_time)
            time_avg = r2(time_sum/direct_count)
            if payload[5] > r2(float(parsedline[1])):
                time_max = r2(float(payload[5]))
            else:
                time_max = r2(float(parsedline[1]))
            newpayload = (direct_count, count_perc, time_sum, time_perc, time_avg, time_max, time_med, all_count)
            d[parsedline[0]] = newpayload

    yield d
#    return d


lines = get_lines(my_log)
parsed = parse_line(lines)
dicted = get_statistics(parsed)


#d = dict()
#for par in parsed:
#    print(get_statistics(par))



d = dict()

for dic in dicted:
    print(dic)
#    pass
print(len(dic))


with open("report.txt", "w") as report:
    for i in dic:
        report.write(i + " " + str(dic[i]) + '\n')


def main():
    pass

if __name__ == "__main__":
    main()
