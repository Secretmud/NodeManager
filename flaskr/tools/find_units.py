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
        self.timeout = 1
        ssh_total = 0
        active_total = 0
        self.subnet = ""

    def set_ip(self, ip_list):
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
        pool = mp.Pool(processes=len(self.ip))
        for i in range(0, len(self.ip)):
            ip = self.ip[i].rsplit('.', 1)
            active = pool.map(self.active_machines, self.ip)
            active = [i for i in active if i is not None]
            ssh = pool.map(self.locate_ssh, active)
            ssh = [i for i in ssh if i is not None]
        return active, ssh

    def active_machines(self, ip):
        respone = None
        try:
            respone = subprocess.check_output(["ping", "-c", "1", "-w", "1", ip],
                                              stderr=subprocess.STDOUT,
                                              universal_newlines=True)
            return ip
        except subprocess.CalledProcessError:
            respone = subprocess.CalledProcessError.stdout

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
            print(f"Couldn't connect to {ip} over port {port[0]}")

    def ping(self, ip):
        import re
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
