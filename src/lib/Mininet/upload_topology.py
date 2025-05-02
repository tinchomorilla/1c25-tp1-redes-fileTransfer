import time
from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.term import makeTerm  # <-- para abrir xterm

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

    print("*** SLEEPING 10 SECONDS TO START WIRESHARK")
    time.sleep(10)

    print("*** Launching terminals with commands")

    makeTerm(h1, cmd="bash -c 'python3 src/start_server.py -H 10.0.0.1 -p 9000 -s src/lib/Server/downloads; exec bash'")
    makeTerm(h2, cmd="bash -c 'python3 src/upload.py -H 10.0.0.1 -p 9000 -s src/lib/Client/uploads/momo.jpeg -n momo.jpeg -r stop-and-wait; exec bash'")

    print("*** Running CLI")
    CLI(net)

    print("*** Stopping network")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    customTopo()
