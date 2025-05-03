from typing import Any, cast
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import Node
from mininet.topo import Topo
from mininet.link import TCLink
import argparse

class Router(Node):
    def config(self, *args: Any, **kwargs: Any) -> dict:
        result = super().config(*args, **kwargs)
        self.cmd("sysctl -w net.ipv4.ip_forward=1")
        return result

    def terminate(self):
        self.cmd("sysctl -w net.ipv4.ip_forward=0")
        super().terminate()


class FragmentationTopo(Topo):
    def __init__(self, mtu: int, loss: int):
        self.mtu = mtu
        self.loss = loss
        super().__init__()

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
        
        if self.loss > 0:
            self.addLink(h2, s3, cls=TCLink, loss=self.loss)
        else:
            print("No se aplicará pérdida de paquetes en el enlace entre s3 y h2")
            self.addLink(h2, s3)


def run(mtu: int, loss: int):
    topo = FragmentationTopo(mtu=mtu, loss=loss)
    net = Mininet(topo=topo, link=TCLink)
    net.start()

    s2 = cast(Node, net.get("s2"))
    h1 = cast(Node, net.get("h1"))
    h2 = cast(Node, net.get("h2"))


    if mtu > 0:
        s2.cmd(f"ifconfig s2-eth2 mtu {mtu}")

    h1.cmd("sysctl -w net.ipv4.ip_no_pmtu_disc=1")
    h2.cmd("sysctl -w net.ipv4.ip_no_pmtu_disc=1")

    h1.cmd("sysctl -w net.ipv4.tcp_mtu_probing=0")
    h2.cmd("sysctl -w net.ipv4.tcp_mtu_probing=0")

    try:
        CLI(net)
    finally:
        net.stop()


if __name__ == "__main__":
    setLogLevel("info")

    parser = argparse.ArgumentParser(description="Simulación de fragmentación IPv4 en Mininet")
    parser.add_argument("--mtu", type=int, default=600, help="Tamaño del MTU en s2-eth2 (ej: 600)")
    parser.add_argument("--loss", type=int, default=0, help="Porcentaje de pérdida en el enlace entre s3 y h2 (ej: 10)")
    args = parser.parse_args()

    run(mtu=args.mtu, loss=args.loss)
