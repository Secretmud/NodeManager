import socket
from socket import *
import time
import subprocess
import multiprocessing as mp


class Singleton(type):
    _instance = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instance:
            cls._instance[cls] = super.__call__(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance[cls]


class UnitSearch(metaclass=Singleton):

    def __init__(self):
        self.ip = []
        self.timeout = 0.2
        ssh_total = 0
        active_total = 0
        self.subnet = ""

    def set_ip(self, ip_list):
        context = ip_list
        if ":" in context:
            context = context.split(":")
            ip = context[0].split(".")
            print(ip)
            print(context)
            self.ip = [f"{ip[0]}.{ip[1]}.{ip[2]}.{i}" for i in range(int(ip[3]), 2**(32-int(context[1]))-1)]
        else:
            self.ip = ip_list

    def set_timeout(self, timeout):
        self.timeout = timeout

    def set_subnet(self, subnet):
        self.subnet = subnet

    """
    parallel_calls - creates a CPU pool, and checks active IPs in the range
    supplied. It also checks if any has ssh available. This will be used 
    to generate some jobs at a later point.
    """

    def parallel_calls(self):
        from time import perf_counter
        from multiprocessing import Pool
        pool = Pool()
        start = perf_counter()
        ip = pool.map(self.active_machines, self.ip)
        ip = [i for i in ip if i is not None]
        print(ip)
        ssh = pool.map(self.locate_ssh, ip)
        print(ssh)

        time_taken = perf_counter() - start
        return ip, ssh, time_taken

    def active_machines(self, ip):
        respone = None
        import os
        if os.system(f"ping -c 1 {ip}") == 0:
            return ip
            """
        s = socket(AF_INET, SOCK_STREAM)
        s.settimeout(self.timeout)
        try:
            conn = s.connect((ip, 1))
            s.close()
            return ip
        except error:
            pass
            """

    def locate_ssh(self, ip):
        s = socket(AF_INET, SOCK_STREAM)
        s.settimeout(self.timeout)
        port = []
        port.append(22)
        try:
            conn = s.connect((ip, port[0]))
            s.close()
            return ip
        except error:
            pass

    def ping(self, ip):
        import re
        print(ip)
        try:
            result = subprocess.run(
                # Command as a list, to avoid shell=True
                ['ping', '-c', '1', ip],
                # Expect textual output, not bytes; let Python .decode() on the fly
                text=True,
                # Shorthand for stdout=PIPE stderr=PIPE etc etc
                capture_output=True,
                # Raise an exception if ping fails (maybe try/except it separately?)
                check=True)
            for line in result.stdout.splitlines():
                if "icmp_seq" in line:
                    timing = line.split('time=')[-1].split(' ms')[0]
                    print(ip, timing)
                    return timing
            return "Nan"
        except subprocess.CalledProcessError:
            return 1


if __name__ == '__main__':
    startTime = time.time()
    target = UnitSearch()
    target.set_ip([f"192.168.1.{i}" for i in range(1, 255)])
    target.parallel_calls()
    print(f"{time.time() - startTime}")
    print(f"{target.ssh_total} {target.active_total}")
