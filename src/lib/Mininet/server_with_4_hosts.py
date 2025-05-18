import argparse
from time import sleep
from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.term import makeTerm


def customTopo(protocol):
    net = Mininet(link=TCLink)

    print("*** Adding controller")
    net.addController("c0")

    print("*** Adding hosts")
    server = net.addHost("h1", ip="10.0.0.1/24")
    clients = []
    for i in range(4):
        client = net.addHost(f'h{i+2}', ip=f'10.0.0.{i+2}/24')  # h2 to h5
        clients.append(client)

    print("*** Adding switch")
    s1 = net.addSwitch("s1")

    print("*** Creating links with 10% packet loss")
    net.addLink(server, s1, loss=10)
    for client in clients:
        net.addLink(client, s1)  # loss=10

    print("*** Starting network")
    net.start()

    print("*** Launching server terminal")
    makeTerm(
        server,
        cmd=f"bash -c 'python3 src/start_server.py -H 10.0.0.1 -p 9000 -s src/lib/Server/downloads -r {protocol} -v; exec bash'",
    )

    sleep(1)  # Wait for server to start

    print("*** Launching client terminals")
    # --- Uploads (h2 and h3) ---
    for idx in range(2):
        src_file = "src/lib/Client/uploads/5MB.pdf"
        dest_file = f"upload_copia_{idx+1}.pdf"
        makeTerm(
            clients[idx],
            cmd=f"bash -c 'python3 src/upload.py -H 10.0.0.1 -p 9000 -s {src_file} -n {dest_file} -r {protocol} -v; exec bash'",
        )

    # --- Downloads (h4 and h5) ---
    for idx in range(2, 4):
        download_path = f"src/lib/Client/downloads/5MB_CLIENT_{idx+1}.pdf"
        remote_filename = "5MB.pdf"
        makeTerm(
            clients[idx],
            cmd=f"bash -c 'python3 src/download.py -H 10.0.0.1 -p 9000 -d {download_path} -n {remote_filename} -r {protocol} -v; exec bash'",
        )

    print("*** Running CLI")
    CLI(net)

    print("*** Stopping network")
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    parser = argparse.ArgumentParser(description="Upload Topology")
    parser.add_argument("--r", type=str, help="Protocol to use", default="saw")
    args = parser.parse_args()

    customTopo(args.r)
