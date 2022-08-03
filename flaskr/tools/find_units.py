import socket
from socket import *
import time
import subprocess
import multiprocessing as mp


class UnitSearch():

    def __init__(self):
        self.ip = []
        self.timeout = 0.2
        ssh_total = 0
        active_total = 0
        self.subnet = ""

    def set_ip(self, ip_list):
        context = ip_list
        import ipaddress
        if ":" in context and "www" not in context:
            context = context.replace(":", "/")
            for addr in ipaddress.IPv4Network(context):
                self.ip.append(str(addr))
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

    def locate_ssh(self, ip):
        s = socket(AF_INET, SOCK_STREAM)
        s.settimeout(self.timeout)
        port = [22]
        try:
            conn = s.connect((ip, port[0]))
            s.close()
            return ip
        except error:
            pass

    def ping(self, ip):
        import os
        if os.system(f"ping -c 1 {ip}") == 0:
            return f"Reached"


if __name__ == '__main__':
    startTime = time.time()
    target = UnitSearch()
    target.set_ip([f"192.168.1.{i}" for i in range(1, 255)])
    target.parallel_calls()
    print(f"{time.time() - startTime}")
    print(f"{target.ssh_total} {target.active_total}")
