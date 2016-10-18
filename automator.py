import ConfigParser
import time
import multiprocessing
import os
import sys

from browser import get_browser
from browser import rp_login as login
from browser import rp_logout as logout
# from concurrent import futures
from requests.exceptions import ReadTimeout

CPU_CORE = multiprocessing.cpu_count()
EFFECTIVE_CPU_THREAD = 2*CPU_CORE + 1
CONFIG_FILE = "/etc/gluu/cluster-benchmark.ini"


def do_login(browser, base_url, username, password, timeout=None):
    login_page = login(browser, base_url, username, password, verify_ssl=False,
                       timeout=timeout)
    return ("inum" in login_page.text)


def do_logout(browser, base_url, timeout=None):
    logout_page = logout(browser, base_url, verify_ssl=False, timeout=timeout)
    return ("inum" not in logout_page.text)


def unitbench(base_url, username, password, timeout=None):
    browser = get_browser()
    try:
        login_status = do_login(browser, base_url, username, password,
                                timeout=timeout)
    except ReadTimeout:
        login_status = False

    time.sleep(1)

    try:
        logout_status = do_logout(browser, base_url, timeout=timeout)
    except ReadTimeout:
        logout_status = False
    return (login_status, logout_status)


def get_config(configfile):
    """Loads config from a file.

    Example of a config file:

        [benchmark]
        password = my-secret-password
        base_url = https://my.cluster.local
    """
    parser = ConfigParser.SafeConfigParser()
    parser.read(configfile)

    config = {
        "password": parser.get("benchmark", "password"),
        "base_url": parser.get("benchmark", "base_url"),
    }
    return config


def main():
    if not os.path.isfile(CONFIG_FILE):
        print "missing config file {}".format(CONFIG_FILE)
        sys.exit(1)

    try:
        config = get_config(CONFIG_FILE)
    except ConfigParser.NoSectionError:
        print "missing benchmark section in {}".format(CONFIG_FILE)
        sys.exit(1)
    except ConfigParser.NoOptionError as exc:
        print "missing {} option under {} section in {}".format(
            exc.option, exc.section, CONFIG_FILE,
        )
        sys.exit(1)

    try:
        data = [
            (config["base_url"], 'user_'+str(i), config["password"], 10,)
            for i in xrange(1000000000, 1000000010)
        ]

        for args in data:
            print unitbench(*args)

        # with futures.ThreadPoolExecutor(max_workers=EFFECTIVE_CPU_THREAD) as executor:
        #     result = executor.map(lambda args: unitbench(*args), data)

        # for i, r in enumerate(result):
        #     print 'user: {}, result: {}'.format(data[i][1], r)
    except KeyboardInterrupt:
        print "canceled by user"
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
