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
        url = string.split('"')[1]
        time = string.split(" ")[-1].replace("\n","")
        yield url, time


def get_lines(file):
#    open = open if file.extension == "" else gzip.open

    if file.extension == "gz":
        log = gzip.open(file.path, 'rb')
    else:
        log = open(file.path, 'r+', encoding='utf-8')
    for line in log:
        yield(line)


def get_statistics(parsedlines):
    for parsedline in parsedlines:
        if d.get(parsedline[0]) is None:
            i = 1
            d.update( {parsedline[0] : (parsedline[1], i)} )
        else:
#            print(d.get(parsedline[0]))
            payload = d.get(parsedline[0])
#            print(payload)
            newpayload = (float(payload[1]) + float(parsedline[1]), int(payload[1]) + 1)
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
#    print(dic)
    pass
print(len(dic))


with open("report.txt", "w") as report:
    for i in dic:
        report.write(i + " " + str(dic[i]) + '\n')


def main():
    pass

if __name__ == "__main__":
    main()
