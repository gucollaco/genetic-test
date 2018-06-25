import time


def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        t = (time2-time1)*1000.0
        if t > 0:
            print('                                                                                                   '
                  '                  {} ms'.format(t))
        return ret
    return wrap


def timing_open():
    return time.time()


def timing_close(t):
    print('                                                                           %0.3f ms' % ((time.time() - t) * 1000.0))