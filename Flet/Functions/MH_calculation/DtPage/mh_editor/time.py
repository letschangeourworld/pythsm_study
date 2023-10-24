import time

def time_calc():
    timestamp = time.time()
    it = time.localtime(timestamp)
    formatted = time.strftime("%Y-%m-%d %H:%M:%S", it)
    return formatted
