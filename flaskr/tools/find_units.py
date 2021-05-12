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
        self.start_ip = "" 
        self.subnet = ""
        ssh_total = 0
        active_total = 0

    def set_ip(self, ip):
        self.start_ip = ip

    def set_subnet(self, subnet):
        self.subnet = subnet

    """
    parallel_calls - creates a CPU pool, and checks active IPs in the range
    supplied. It also checks if any has ssh available. This will be used 
    to generate some jobs at a later point.
    """
    def parallel_calls(self):
        cpu = mp.cpu_count()
        pool = mp.Pool(processes=100)
        ip = self.start_ip.rsplit('.', 1)
        ips = [ip[0] + "." + str(i) for i in range(int(ip[1]), 255)]
        active_t = time.time()
        active = pool.map(self.active_machines, ips)
        self.active_total = time.time() - active_t
        active = [i for i in active if i is not None]
        ssh_t = time.time()
        ssh = pool.map(self.locate_ssh, active)
        self.ssh_total = time.time() - ssh_t
        ssh = [i for i in ssh if i is not None]
        return (active, ssh)

    def locate_ssh(self, ip):
        s = socket(AF_INET, SOCK_STREAM)
        s.settimeout(1)
        try:
            conn = s.connect((ip, 22))
            s.close()
            return ip
        except:
            return None

    def active_machines(self, ip):
        try:
            respone = subprocess.check_output(["ping", "-c", "1", "-w", "1",  ip],
                                              stderr=subprocess.STDOUT,
                                              universal_newlines=True)
            return ip
        except subprocess.CalledProcessError:
            respone = None


if __name__ == '__main__':
    startTime = time.time()
    target = UnitSearch("192.168.1.1", "255.255.255.1")
    target.parallel_calls()
    print(f"{time.time() - startTime}")
    print(f"{target.ssh_total} {target.active_total}")
