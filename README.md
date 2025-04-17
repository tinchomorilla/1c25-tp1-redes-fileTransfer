# TP1


## 6. Anexo: Fragmentación IPv4

### Objetivo del trabajo

Comprender y comprobar empíricamente:

- El proceso de fragmentación en IPv4.
- El comportamiento de TCP y UDP ante la pérdida de fragmentos.
- El aumento de tráfico causado por la reducción del MTU en la red.

La red se emula usando Mininet, y se analiza el tráfico con iperf y Wireshark.

### Preparación del entorno
Instalar Mininet, iperf y Wireshark:
```bash
sudo apt update
sudo apt install mininet iperf wireshark
```

### Topología de la red

```
h1 --- s1 --- s2 --- s3 --- h2
```

- 2 hosts (h1 y h2)
- 3 switches conectados linealmente (s1, s2, s3)
- s2 tendrá una interfaz con MTU reducida
- s3 tendrá una interfaz con pérdida de paquetes

### Pasos para reproducir

#### 1.  Levantar la red

```bash
sudo mn --custom fragmentacion.py --topo fragmentation_topo
```

#### 2.  Verificar conectividad  básica

```bash
mininet> h1 ping h2
```

#### 3. Forzar la fragmentacion reduciendo el MTU de s2

```bash
mininet> s2 ifconfig s2-eth1 mtu 500
```

#### 4.  Simular la pérdida de paquetes en s3

```bash
mininet> s3 tc qdisc add dev s3-eth1 root netem loss 10%
```

#### 5. Ejecutar pruebas con iperf

##### UDP sin fragmentación
```bash
mininet> h2 iperf -s -u &
mininet> h1 iperf -c h2 -u -l 400 -t 10
```

##### TCP sin fragmentación
```bash
mininet> h2 iperf -s &
mininet> h1 iperf -c h2 -l 400 -t 10
```

##### UDP con fragmentación
(usar tamaño mayor al MTU reducido)
```bash
mininet> h1 iperf -c h2 -u -l 1500 -t 10
```
##### TCP con fragmentación
```bash
mininet> h1 iperf -c h2 -l 1500 -t 10
```
