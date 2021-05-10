from socket import *
import time
startTime = time.time()

class UnitSearch:

    def __init__(self, iprange, subnet):
        self.iprange = iprange
        self.subnet = subnet


    def locate_ssh(self):
        startTime = time.time()
        ips = []
        ip = self.iprange.rsplit('.', 1)
        print(ip)
        for i in range(int(ip[1]), 255):
            s = socket(AF_INET, SOCK_STREAM)
            address = ip[0] + "." + str(i)
            conn = s.connect_ex((address, 22))
            if (conn == 0):
                ips.append(address)
            s.close()
            print(f"{i}", end="\r")

        print(ips)
        print('Time taken:', time.time() - startTime)

if __name__ == '__main__':
   target = UnitSearch("192.168.1.1", "255.255.255.1")
   target.locate_ssh()
