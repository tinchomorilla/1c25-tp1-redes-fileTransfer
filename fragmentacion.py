from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI
import time

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
    # net = Mininet(topo=topo, link=TCLink)

    net = Mininet(topo=topo, link=TCLink, controller=None, autoSetMacs=True, autoStaticArp=True)
    net.start()

    # Modo bridge para switches (sin controlador)
    for switch in net.switches:
        switch.cmd("ovs-vsctl set-fail-mode {} standalone".format(switch.name))
    net.start()

    print("*** Aplicando configuraciones de red y levantando servidor en H2")
    s2 = net.get('s2')
    s2.cmd("ifconfig s2-eth1 mtu 500")  # Reducir MTU para forzar fragmentación
    s3 = net.get('s3')
    s3.cmd("tc qdisc add dev s3-eth1 root netem loss 10%")  # Simular pérdida de paquetes

    h2 = net.get('h2')
    h2.cmd("iperf -s -u &")  # Levantar servidor UDP

    # print("*** Iniciando captura de tráfico, sleeping")
    # #s2.cmd("udpdump -i s2-eth1 -w /tmp/fragmentacion.pcap &") # Captura de tráfico en s2
    # time.sleep(10)

    # h1 = net.get('h1')
    # # h1.cmd("iptables -t mangle -A OUTPUT -p udp -j DF --clear")  # Eliminar DF para permitir fragmentación

    # print("*** Enviando tráfico UDP desde h1 a h2")
    # h1.cmd("iperf -c 10.0.0.2 -u -l 2000 -t 10")

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
