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
     m = re.match('^\D*-\d{8}($|.gz$)', file)
     if m is not None:
         if file > last:
             last = file
#             print(last)
             date = file.split("-")[-1].split(".")[0]
#             path = os.path.abspath(last)
             path = str(os.path.abspath(config["LOG_DIR"])) + "/"  + last
#             path = str(os.listdir(config["LOG_DIR"])) + last
             extension = "gz" if last.split(".")[-1] == "gz" else ""

#print(last)
#print(date)
#print(path)
#print(extension)

Lastlog = namedtuple('Lastlog', 'date path extension')
my_log = Lastlog(date, path, extension)

print(*my_log)


open = open if my_log.extension == "" else gzip.open
with open(my_log.path, 'r+', encoding='utf-8') as log:
    for line in log.readlines():
        print(line)
log.close()


def main():
    pass

if __name__ == "__main__":
    main()
