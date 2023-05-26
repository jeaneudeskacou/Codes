import os
from enum import Enum

LOG_DIR = r"C:\local_Documents\logs\opr204"
OUTPUT_DIR = r"C:\local_Documents\out"
TRACE_FILE_NAME = "arbopr_openreport_trace.log"
LOG_FILE_NAME = "arbopr_openreport.log"
TRACE_PATH = os.path.join(LOG_DIR, TRACE_FILE_NAME)
LOG_PATH = os.path.join(LOG_DIR, LOG_FILE_NAME)
TABLE_MARKER = "Start log content for table"
BAD_LINE = "|com.orange.srs"
OUTPUT_FILE_EXTENTION = "txt"
LOG_LEVEL_ENUM = Enum("LOG_LEVEL", ['INFO', 'DEBUG'])
LOG_LEVEL = LOG_LEVEL_ENUM.INFO
# TRACE_PATH = r"C:\OpenStat\workspace-openstat\OpenStat\openstat-parent\domain\logs\arbopr_openreport_trace.log"
# LOG_PATH = r"C:\OpenStat\workspace-openstat\OpenStat\openstat-parent\domain\logs\arbopr_openreport.log"
STAT_DIR = r"C:\OpenStat\workspace-openstat\OpenStat\openstat-parent\arbopr\src\main\resources\global\computation\V1_0"
START_GENERATE_REPORT_MARKER = "[generateReportWithResultObject] Start"
END_GENERATE_REPORT_MARKER = "[generateReportWithResultObject] End"
START_KEY = "START_TIMESTAMP"
END_KEY = "END_TIMESTAMP"
TABLES = "TABLES"
STAT_FILES = [
    "STAT_REPORT_1363.xml",
    "STAT_REPORT_1364.xml",
    "STAT_REPORT_1361.xml",
    "STAT_REPORT_1360.xml",
    "STAT_REPORT_1359.xml",
    "STAT_REPORT_1358.xml"
]