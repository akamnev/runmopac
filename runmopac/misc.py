import os
import logging

def get_log(log_dir, log_name):
    log = logging.getLogger(log_name)
    log.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    f = logging.FileHandler(
        os.path.join(log_dir, log_name + '.log'), 'a')
    f.setFormatter(formatter)
    log.addHandler(f)

    c = logging.StreamHandler()
    c.setFormatter(formatter)
    log.addHandler(c)
    return log
