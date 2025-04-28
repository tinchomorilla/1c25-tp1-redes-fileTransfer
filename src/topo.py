from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel

def customTopo():
    net = Mininet(link=TCLink)

    print("*** Adding controller")
    net.addController('c0')

    print("*** Adding hosts")
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')

    print("*** Adding switch")
    s1 = net.addSwitch('s1')

    print("*** Creating links with 10% packet loss")
    net.addLink(h1, s1, loss=10)
    net.addLink(h2, s1, loss=10)

    print("*** Starting network")
    net.start()

    print("*** Running CLI")
    CLI(net)

    print("*** Stopping network")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    customTopo()
