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



lines = get_lines(my_log)
parsed = parse_line(lines)

for par in parsed:
    print(par)

def main():
    pass

if __name__ == "__main__":
    main()
