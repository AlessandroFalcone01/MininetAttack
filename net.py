from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.node import RemoteController, Host
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from subprocess import Popen
from time import sleep
import csv
from .topo import CustomTopology
import matplotlib.pyplot as plt
from copy import copy


class Net:

    def __init__(self):
        self.tmp = 'tmp.txt'
        self.data = {}

    def clear_net(self):
        #Clears evrything going on the network
        info('*** Clearing net... ***')
        cmd = "mn -c"
        Popen(cmd, shell=True).wait()

    def start_net(self):
        topo= CustomTopology()
        controller_ip= '192.168.56.9'
        controller_port= 6633
        self.net = Mininet(topo=topo, controller=lambda name: RemoteController(name, ip=controller_ip, port=controller_port))
        self.net.start()
        #STP protocol
        for i in range (1,4):
            switch_name= f's{i}'
            switch= self.net.get(switch_name)
            switch.cmd(f'ovs-vsctl set bridge switch{switch_name} stp-enable=true')
        print("dumoing host connections")
        dumpNodeConnections(self.net.hosts)
        #Testing network 
        self.net.pingAll()
        self.net.pingAll()

    def stop_net(self):
        info('*** stopping net ***\n')
        self.net.stop()

    #Monitoro la rete (quantità di dati trsmeessi/ricevuti per unità di tempo) e salvo i dati su un file
    def start_monitor(self):
        info('*** Start monitor ***\n')
        cmd = f"bwm-ng -o csv -T rate -C ',' > {self.tmp} &"
        Popen(cmd, shell=True).wait()

    #Smetto di monitorare la rete
    def stop_monitor(self):
        info('*** Stop monitor ***\n')
        cmd = "killall bwm-ng"
        Popen(cmd, shell=True).wait()

    #Leggo il file csv e carico le informazioni che mi servono in data
    def fill_data(self):
        with open(self.tmp) as csvf:
            csvr = csv.reader(csvf, delimiter=',')
            for row in csvr:
                key = row[1]
                tme = float(row[0])
                load = float(row[4]) * 8
                if key in self.data:
                    self.data[key]['time'].append(tme)
                    self.data[key]['load'].append(load)
                else:
                    self.data[key] = {}
                    self.data[key]['time'] = []
                    self.data[key]['load'] = []


    #L'host 1 attaccherà 2 e l'host 3 attaccherà 4
    def start_attack(self):
        info('*** starting attack ***')

        #host che attaccheranno
        h1= self.net.get('h1')
        h3= self.net.get('h3')
        ip2= self.net.get('h2').IP()
        ip4= self.net.get('h4').IP()
        
        #attacco
        h1.cmd(f"hping3 {ip2} --flood --udp &")
        h3.cmd(f"hping3 {ip4} --flood --udp &")
        

    #Fermo l'attacco
    def stop_attack(self):
        info('*** stopping attack ***')
        cmd= "killall hping3"
        Popen(cmd, shell=True).wait()

    #Creo un garfico a dispersione e lo salvo come immagine
    def plot_latency_for_all_switches(self, output_file):
        info('*** Printing data ***\n')
        for switch_key in self.data.keys():
            values = self.data[switch_key]
            plt.scatter(values['time'], values['load'], label=f'{switch_key} - Load', alpha=0.5)

        plt.legend()
        plt.xlabel('Time')
        plt.ylabel('Load')
        plt.title('Load over Time for Each Switch')
        plt.savefig(output_file)

    def check_host_connettivity(self, host, target):
        h= self.net.get(host)
        ip_target= self.net.get(target).IP()
        
        output= h.cmdPrint(f"ping -c 15 {ip_target}")
        print(output)

    def main(self):
        setLogLevel('info')
        self.start_net()
        self.start_monitor()
        sleep(5)    #Durata del monitoring prima dell'attacco
        self.start_attack()
        sleep(10)    #Durata del monitoring durante l'attacco
        self.stop_attack()
        sleep(5)    #Durata del monitoring dopo aver stoppato l'attacco
        self.stop_monitor()
        self.fill_data()
        self.plot_latency_for_all_switches('all_switches.png')
        self.stop_net()


if __name__ == '__main__':
    n= Net()
    n.main()