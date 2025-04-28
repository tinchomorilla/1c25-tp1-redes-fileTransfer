# #!/usr/bin/python

# from mininet.net import Mininet
# from mininet.node import OVSKernelSwitch, RemoteController
# from mininet.link import TCLink
# from mininet.cli import CLI
# from mininet.log import setLogLevel

# def simpleTopo():
#     net = Mininet(controller=None, switch=OVSKernelSwitch, link=TCLink)

#     print("* Creating nodes")
#     server = net.addHost('server')
#     client = net.addHost('client')
#     switch = net.addSwitch('s1')

#     print("* Creating links with 10% packet loss")
#     net.addLink(server, switch, loss=10)  # 10% de pérdida en enlace server-switch
#     net.addLink(client, switch, loss=10)  # 10% de pérdida en enlace client-switch

#     print("* Starting network")
#     net.start()

#     print("* Assigning IPs manually")
#     server.setIP('10.0.0.1/24')
#     client.setIP('10.0.0.2/24')

#     print("* Ready. Start your server and client manually from Mininet CLI.")
#     CLI(net)

#     print("* Stopping network")
#     net.stop()

# if __name__ == '__main__':
#     setLogLevel('info')
#     simpleTopo()

from mininet.net import Mininet
from mininet.node import Host, OVSKernelSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel
import time

def run():
    net = Mininet(link=TCLink)

    print("* Creando nodos")
    server = net.addHost('server')
    client = net.addHost('client')
    switch = net.addSwitch('s1')

    print("* Creando enlaces con 10% de pérdida")
    net.addLink(server, switch, loss=10)
    net.addLink(client, switch, loss=10)

    print("* Asignando IPs")
    server.setIP('10.0.0.1/24')
    client.setIP('10.0.0.2/24')

    print("* Iniciando red")
    net.start()

    # print("* Creando carpetas necesarias")
    # server.cmd('mkdir -p downloads')
    # client.cmd('mkdir -p uploads')

    # print("* DURMIENDO 10 SEGS")
    # time.sleep(15)

    # print("* Copiando archivos al cliente (simulado)")
    # # Esto depende de que tengas el archivo localmente, o lo podés copiar manualmente
    # client.cmd('cp /home/kaki/Escritorio/fiuba/tps_redes/src/Stop-and-wait/uploads/momo.jpeg uploads/momo.jpeg')

    # print("* Lanzando servidor")
    # server.cmd('python3 start_server.py -H 10.0.0.1 -p 9000 -s ./downloads &')
    # time.sleep(2)  # Dejar que el server arranque bien

    # print("* Lanzando cliente")
    # client.cmd('python3 upload.py -H 10.0.0.1 -p 9000 -s ./uploads/momo.jpeg -n copia_mininet.jpeg &')

    # print("* Listo, podés abrir CLI si querés investigar o tcpdump")
    CLI(net)

    print("* Cerrando red")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()