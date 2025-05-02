from typing import Any, cast
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import Node
from mininet.topo import Topo
from mininet.link import TCLink

class Router(Node):
    def config(self, *args: Any, **kwargs: Any) -> dict:
        result = super().config(*args, **kwargs)
        self.cmd("sysctl -w net.ipv4.ip_forward=1")
        return result

    def terminate(self):
        self.cmd("sysctl -w net.ipv4.ip_forward=0")
        super().terminate()


class FragmentationTopo(Topo):
    def build(self, **_opts):
        s2 = self.addNode("s2", cls=Router, ip=None)
        s1, s3 = [self.addSwitch(s) for s in ("s1", "s3")]

        

        self.addLink(s1, s2, intfName2="s2-eth1",
                     params2={"ip": "10.0.0.1/30"})
        self.addLink(s3, s2, intfName2="s2-eth2",
                     params2={"ip": "10.0.0.5/30"})

        h1 = self.addHost("h1", ip="10.0.0.2/30", defaultRoute="via 10.0.0.1")
        h2 = self.addHost("h2", ip="10.0.0.6/30", defaultRoute="via 10.0.0.5")

        self.addLink(h1, s1)
        self.addLink(h2, s3)

        # self.addLink(h2, s3, loss = 10)

def run():
    topo = FragmentationTopo()
    net = Mininet(topo=topo)
    net.start()

    s2 = cast(Node, net.get("s2"))
    h1 = cast(Node, net.get("h1"))
    h2 = cast(Node, net.get("h2"))

    # Set s2-s2 MTU to 600 bytes
    s2.cmd("ifconfig s2-eth2 mtu 600")

    # Unset DF bit
    h1.cmd("sysctl -w net.ipv4.ip_no_pmtu_disc=1")
    h2.cmd("sysctl -w net.ipv4.ip_no_pmtu_disc=1")

    # Disable TCP MTU probing
    h1.cmd("sysctl -w net.ipv4.tcp_mtu_probing=0")
    h2.cmd("sysctl -w net.ipv4.tcp_mtu_probing=0")

    CLI(net)
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    run()
