from mininet.net import Mininet
from mininet.node import Host, OVSKernelSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel
import time

SERVER_CMD = "python3 src/Server/start_server.py -H 10.0.0.1 -p 9000 -s src/Server/downloads"
CLIENT_CMD = "python3 src/Client/main.py upload -H 10.0.0.1 -p 9000 -s src/Client/uploads/momo.jpeg -n momo.jpeg -r stop-and-wait"
SERVER_IP = "10.0.0.1/24"
CLIENT_IP = "10.0.0.2/24"

def run():
    net = Mininet(link=TCLink)
    try:
        print("* Creando nodos")
        server = net.addHost('server')
        client = net.addHost('client')
        switch = net.addSwitch('s1')

        print("* Creando enlaces con 10% de pérdida")
        net.addLink(server, switch, loss=0)
        net.addLink(client, switch, loss=0)

        print("* Asignando IPs")
        server.setIP(SERVER_IP)
        client.setIP(CLIENT_IP)

        print("* Iniciando red")
        net.start()

        print("* Esperando 3 segundos para que la red esté lista")
        time.sleep(3)

        # print("* Iniciando servidor en background (salida a server_output.log)")
        # server.cmd(SERVER_CMD)

        # print("* Esperando 2 segundos para que el server esté escuchando")
        # time.sleep(2)

        # print("* Verificando si el servidor se inició correctamente...")
        # server_output = server.cmd('cat server_output.log')
        # if '[SERVER] Escuchando' not in server_output:
        #     print("\n🚨 ERROR: El servidor NO se inició correctamente. Revisa server_output.log\n")
        #     print(server_output)
        #     net.stop()
        #     return

        # print("* Servidor iniciado correctamente ✅")

        # print("* Iniciando cliente")
        # client.cmdPrint(CLIENT_CMD)

        # print("* Test finalizado. Entrando a la CLI")
        CLI(net)

    finally:
        net.stop()
if __name__ == '__main__':
    setLogLevel('info')
    run()