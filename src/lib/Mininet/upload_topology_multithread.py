import argparse
import time
from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.term import makeTerm  # <-- para abrir xterm

def customTopo(protocol):
    net = Mininet(link=TCLink)

    print("*** Adding controller")
    net.addController('c0')

    print("*** Adding hosts")
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.0.3/24')
    h4 = net.addHost('h4', ip='10.0.0.4/24')

    print("*** Adding switch")
    s1 = net.addSwitch('s1')

    print("*** Creating links with 10% packet loss")
    net.addLink(h1, s1, loss=10)
    net.addLink(h2, s1, loss=10)

    print("*** Adding switch")
    s2 = net.addSwitch('s2')

    net.addLink(h1, s2, loss=10)
    net.addLink(h3, s2, loss=10)

    print("*** Adding switch")
    s3 = net.addSwitch('s3')

    net.addLink(h1, s3, loss=10)
    net.addLink(h4, s3, loss=10)

    print("*** Starting network")
    net.start()

    #print("*** SLEEPING 10 SECONDS TO START WIRESHARK")
    #time.sleep(10)

    print("*** Launching terminals with commands")

    makeTerm(h1, cmd=f"bash -c 'python3 src/start_server.py -H 10.0.0.1 -p 9000 -s src/lib/Server/downloads -r {protocol} -q; exec bash'")
    makeTerm(h2, cmd=f"bash -c 'python3 src/upload.py -H 10.0.0.1 -p 9000 -s src/lib/Client/uploads/5MB.pdf -n 5MB_SERVER1.pdf -r {protocol} -q; exec bash'")
    time.sleep(2)
    makeTerm(h3, cmd=f"bash -c 'python3 src/upload.py -H 10.0.0.1 -p 9000 -s src/lib/Client/uploads/5MB.pdf -n 5MB_SERVER2.pdf -r {protocol} -q; exec bash'")
    time.sleep(2)
    makeTerm(h3, cmd=f"bash -c 'python3 src/upload.py -H 10.0.0.1 -p 9000 -s src/lib/Client/uploads/5MB.pdf -n 5MB_SERVER3.pdf -r {protocol} -q; exec bash'")

    print("*** Running CLI")
    CLI(net)

    print("*** Stopping network")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    parser = argparse.ArgumentParser(description='Upload Topology')
    parser.add_argument('--r', type=str, help='Protocol to use', default='saw')
    args = parser.parse_args()

    customTopo(args.r)
