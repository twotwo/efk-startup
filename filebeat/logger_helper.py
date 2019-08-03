# -*- coding: utf-8 -*-
############################################################
#
# Read logs from stdout, then send to RabbitMQ
#
############################################################
import os
import json
import logging
import logging.handlers

import time
import tzlocal
from datetime import datetime


class LoggerHelper(object):
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger('LoggerHelper')
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        # add formatter to ch
        ch.setFormatter(logging.Formatter('%(message)s'))
        # add ch to logger
        self.logger.addHandler(ch)
        self.localzone = tzlocal.get_localzone()
        self.logger.debug('init LoggerHelper ...')
        return super().__init__(*args, **kwargs)

    def info(self, id):
        create_time = time.time()
        msg = dict({
            "Level": "INFO",
            "HosCode": os.getenv("HOSPITAL_CODE", "DEV00001"),
            "Product": os.getenv("PRODUCT", "ct-lung-logger-helper"),
            "Module": "dlserver",
            "Action": "test",
            "Start": datetime.now(tz=self.localzone).isoformat(),
            "PatientID": id,
            "StudyID": id,
            "SeriesID": id,
            "DisplayID": "N/A",
            "Message": "Perf Test Point",
            "Duration": time.time() - create_time,
            "End": datetime.now(tz=self.localzone).isoformat(),
            "Status": "ok"
        })
        self.logger.info(json.dumps(msg))


def print2console(number):
    logger = LoggerHelper()
    for i in range(number):
        # print('{"Action":"updateInstance","Report":"error","SeriesId":"1.3.12.2.1107.5.1.4.75558.30000019050906063107900028003","InstanceNumber":424,"ImageId":"wadouri:http://192.168.110.127:8000/CT_Lung/61905090606/1.2.392.200036.9125.2.138612190166.20110508000138.20190509001294/1.3.12.2.1107.5.1.4.75558.30000019050906063107900028003/1.3.12.2.1107.5.1.4.75558.30000019050906063107900028427","Level":"INFO","TimeStamp":"2019-07-29T13:31:25+00:00","Id":1279,"Hash":"47e360c52e0de3c276707d450e4d83d6b42301f8","UserAgent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36","Product":"prod","HosCode":"h","Module":"Viewer","StudyId":"1.2.840.113619.2.278.3.2831159160.237.1562370619.292","TraceId":"5655ec"}')
        logger.info(i)


if __name__ == '__main__':
    print2console(1)
