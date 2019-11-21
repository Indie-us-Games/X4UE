import inspect
import os
from datetime import datetime

LOG_ALL = 0
LOG_DEBUG = 1
LOG_INFO = 2
LOG_WARN = 3
LOG_ERROR = 4

DEFAULT_LOG_LEVEL = LOG_INFO
__current_log_level = DEFAULT_LOG_LEVEL


def set_log_level(level):
    global __current_log_level
    if level == "ALL":
        __current_log_level = LOG_ALL
        return

    if level == "DEBUG":
        __current_log_level = LOG_DEBUG
        return

    if level == "INFO":
        __current_log_level = LOG_INFO
        return

    if level == "WARN":
        __current_log_level = LOG_WARN
        return

    if level == "ERROR":
        __current_log_level = LOG_ERROR
        return
    
    # DEFAULT
    __current_log_level = DEFAULT_LOG_LEVEL
    

def debuglog(*values):
    __printlog(*values, level=LOG_DEBUG)

def infolog(*values):
    __printlog(*values, level=LOG_INFO)

def warnlog(*values):
    __printlog(*values, level=LOG_WARN)

def errorlog(*values):
    __printlog(*values, level=LOG_ERROR)


def __loglevel_str(level):
    if level == LOG_DEBUG:
        return "debug"
    if level == LOG_INFO:
        return "info"
    if level == LOG_WARN:
        return "warn"
    if level == LOG_ERROR:
        return "error"

    return "unknown"

def __printlog(*values, level=LOG_DEBUG):

    global __current_log_level

    if level < __current_log_level:
        return

    frame = inspect.currentframe().f_back.f_back

    print(
        "[",
        datetime.now().isoformat(timespec="seconds"),
        "]",
        "[",
        __loglevel_str(level),
        "]",
        "(",
        "F->",
        os.path.basename(frame.f_code.co_filename),
        "/ L->",
        frame.f_lineno,
        "in",
        frame.f_code.co_name,
        ")",
        *values
    )
