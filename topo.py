from mininet.topo import Topo
from mininet.node import RemoteController

class CustomTopology(Topo):
    def build(self):
        # Aggiungiamo uno switch radice e due switch del primo livello
        switch1 = self.addSwitch('s1', protocols='OpenFlow13')
        switch2 = self.addSwitch('s2', protocols='OpenFlow13')
        switch3 = self.addSwitch('s3', protocols='OpenFlow13')

        # Colleghiamo lo switch radice agli altri due
        self.addLink(switch1, switch2)
        self.addLink(switch1, switch3)
        self.addLink(switch2, switch3)

        # Aggiungiamo gli host
        host1 = self.addHost('h1')
        host2 = self.addHost('h2')
        host3 = self.addHost('h3')
        host4 = self.addHost('h4')
        

        # Colleghiamo gli host ai due switch
        self.addLink(host1, switch2)
        self.addLink(host2, switch2)
        self.addLink(host3, switch3)
        self.addLink(host4, switch3)