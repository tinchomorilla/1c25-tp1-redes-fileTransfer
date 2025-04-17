from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI

class FragmentationTopo(Topo):
    def build(self):
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        self.addLink(h1, s1)
        self.addLink(s1, s2)
        self.addLink(s2, s3)
        self.addLink(s3, h2)

def run():
    topo = FragmentationTopo()
    net = Mininet(topo=topo, link=TCLink)
    net.start()

    print("+++ Red levantada")

    # Reducir el MTU en una interfaz en el switch s2
    s2 = net.get('s2')
    s2.cmd("ifconfig s2-eth0 mtu 500")
    print("+++ MTU reducido a 500 bytes en s2-eth0")

    # Simular pérdida de paquetes en la interfaz hacia h2
    s3 = net.get('s3')
    s3.cmd("tc qdisc add dev s3-eth1 root netem loss 10%") 
    print("+++ Packet loss del 10% aplicado en s3-eth1")

    CLI(net)

topos = { "fragmentation_topo" : ( lambda: FragmentationTopo() )}

if __name__ == '_main_':
    setLogLevel('info')
    run()
