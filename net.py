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

    def start_server(self, host):
        info(f'*** starting server on {host} ***\n')
        h= self.net.get(host)
        h.cmd("python3 -m http.server 80 &")

    
    def start_attack(self):
        info('*** starting attack ***\n')

        #host che attaccheranno
        h1= self.net.get('h1')
        h3= self.net.get('h3')
        #host attaccati
        ip2= self.net.get('h2').IP()
        ip4= self.net.get('h4').IP()
        
        #attacco
        h1.cmd(f"hping3 --flood --rand-source --udp -p 80 {ip2} &")
        h3.cmd(f"hping3 --flood --rand-source --udp -p 80 {ip4} &")
        

    #Fermo l'attacco
    def stop_attack(self):
        info('*** stopping attack ***\n')
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

        try:
            setLogLevel('info')
            self.start_net()
            self.start_monitor()
            sleep(5)    #Durata del monitoring prima dell'attacco
            self.start_server('h2')
            sleep(1)
            self.start_server('h4')
            sleep(1)

            info('*** checking connettivity before the attack ***')
            self.check_host_connettivity('h1' , 'h2')
            sleep(1)
            self.check_host_connettivity('h3' , 'h4')
            sleep(1)

            self.start_attack()
            sleep(15)    #Durata del monitoring durante l'attacco

            info('*** checking connettivity after the attack ***')
            self.check_host_connettivity('h1' , 'h2')
            sleep(1)
            self.check_host_connettivity('h3' , 'h4')
            sleep(5)

            self.stop_attack()
            sleep(5)    #Durata del monitoring dopo aver stoppato l'attacco
            self.stop_monitor()
            self.fill_data()
            self.plot_latency_for_all_switches('all_switches.png')
            self.stop_net()
        except KeyboardInterrupt:
            self.stop_attack
            self.stop_net
            self.stop_monitor
            self.clear_net
            


if __name__ == '__main__':
    n= Net()
    n.main()