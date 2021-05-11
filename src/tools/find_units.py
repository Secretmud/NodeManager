from socket import *
import time
import subprocess
import multiprocessing as mp

class UnitSearch:

    def __init__(self, start_ip, subnet):
        self.start_ip = start_ip
        self.subnet = subnet

    """
    parallel_calls - creates a CPU pool, and checks active IPs in the range
    supplied. It also checks if any has ssh available. This will be used 
    to generate some jobs at a later point.
    """
    def parallel_calls(self):
        cpu = mp.cpu_count()
        pool = mp.Pool(processes=cpu)
        ip = self.start_ip.rsplit('.', 1)
        ips = [ip[0] + "." + str(i) for i in range(int(ip[1]), 255)]
        active = pool.map(self.active_machines, ips)
        active = [i for i in active if i is not None]
        ssh = pool.map(self.locate_ssh, active)
        ssh = [i for i in ssh if i is not None]
        return (active, ssh)

    def locate_ssh(self, ip):
        s = socket(AF_INET, SOCK_STREAM)
        conn = s.connect_ex((ip, 22))
        if (conn == 0):
            return ip
        else:
            s.close()

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
