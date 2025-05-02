# TP1 -  - Sistemas Distribuidos (75.43)

## Aplicacion de File Transfer entre hosts Cliente y Servidor

## Dependencias

- Instalar openvswitch y xterm
```sh
sudo apt update
sudo apt install openvswitch-testcontroller
sudo apt install xterm
sudo apt install mininet
```

## Ejecutando el proyecto

- Para correr el script de la topologia en mininet (upload)
```sh
sudo python3 src/lib/Mininet/upload_topology.py
```
- Para correr el script de la topologia en mininet (download)
```sh
sudo python3 src/lib/Mininet/download_topology.py
```

- Ejecutar el servidor
```sh
python3 src/start_server.py -H 127.0.0.1 -p 9000 -s src/lib/Server/downloads -r stop_and_wait
```

- Ejecutar el cliente
  - Upload
```sh
python3 src/upload.py -H 127.0.0.1 -p 9000 -s src/lib/Client/uploads/momo.jpeg -n copia4.jpeg -r stop_and_wait
```
  - Download
```sh
python3 src/download.py -H 127.0.0.1 -p 9000 -d src/lib/Client/downloads/nashe.jpeg -n momo.jpeg -r stop_and_wait
```

- Correr tests
  - Upload
```sh
python3 src/lib/Tests/upload_stress_test.py 
```
  - Download
```sh
python3 src/lib/Tests/download_stress_test.py 
```

## Anexo, Fragmentación IPv4: Objetivo

### Objetivo

Este experimento tiene como objetivo observar y comprender el proceso de fragmentación en IPv4, así como el comportamiento de los protocolos TCP y UDP ante la pérdida de fragmentos, y el impacto del MTU en el volumen de tráfico. Para ello, se diseña una red virtual en Mininet que simula un entorno donde la fragmentación ocurre de manera controlada y medible.

Comprobar empíricamente:
- El proceso de **fragmentación IPv4**.
- El comportamiento de **TCP** y **UDP** ante la pérdida de fragmentos.
- El **aumento de tráfico** al reducirse el MTU mínimo en la red.

Para esto se utiliza:
- **Mininet** para simular la red.
- **iperf** para generar tráfico TCP/UDP.
- **Wireshark** para capturar y analizar los paquetes.

---

## Estructura del experimento

El experimento está completamente automatizado mediante un script de Python que utiliza Mininet para crear la red, aplicar configuraciones, y levantar los servicios necesarios.

### Topología
Se construyó una topología lineal en Mininet conformada por dos hosts (h1 y h2) conectados a través de tres nodos intermedios. El nodo central (s2) se implementó como un router (usando una clase personalizada que habilita el reenvío de paquetes mediante ip_forward), mientras que los extremos (s1 y s3) actúan como switches.


```
h1 --- s1 --- s2 --- s3 --- h2
```

- 2 hosts (`h1`, `h2`)
- 3 switches intermedios
  - Se usa un nodo en lugar de un switch en el centro de la topologia (s2), y a este nodo se le setea que pueda hacer ip-forwarding, ya que esto es lo que lo hace comportarse como un router.
- MTU reducido en una interfaz de `s2`: `s2-eth2`.
- Pérdida de paquetes simulada en una interfaz de `s3`.

---

## Instrucciones paso a paso

### Preparación del entorno

Instalar Mininet, iperf y Wireshark:
```bash
sudo apt update
sudo apt install mininet iperf wireshark
```

Limpiar interfaces  huerfanas
```bash
sudo mn -c
```

### Correr el trabajo

#### 1. Ejecutar el script

```bash
sudo python3 src/anexo.py
```

#### 2. Abrir wireshark

Analizar `s2-eth2` para ver la fragmentacion de paquetes.

#### 3. Enviar trafico

##### UDP
```bash
mininet> h2 iperf -s -u &
mininet> h1 iperf -c h2 -u -l 1400
```

##### TCP
```bash
mininet> h2 iperf -s &
mininet> h1 iperf -c h2 -l 1400
```

El tráfico fue capturado con Wireshark, permitiendo observar fragmentos de paquetes, identificadores IP compartidos, offset de fragmentos y el flag "More Fragments".

### Resultados observados
1. *Proceso de fragmentación*
Al generar tráfico con tamaño mayor al MTU del enlace (600 bytes), Wireshark muestra cómo se divide un paquete en múltiples fragmentos IPv4, identificables por el mismo ID de paquete, campos MF y offsets. La fragmentación es manejada por el router s2.

2. *Comportamiento de TCP ante pérdida de fragmentos*
Al introducir pérdida en el enlace (loss), se observó que TCP retransmite automáticamente el paquete completo cuando falta un fragmento, dado que TCP requiere entrega confiable. Esto implica mayor latencia y tráfico adicional por retransmisiones.

3. *Comportamiento de UDP ante pérdida de fragmentos*
En el caso de UDP, si se pierde uno de los fragmentos, el datagrama completo no puede ser reconstruido y se descarta sin notificación. Esto se refleja en que iperf muestra pérdida de paquetes sin intento de recuperación, ya que UDP no implementa mecanismos de fiabilidad.

4. *Aumento del tráfico al reducirse el MTU*
La reducción del MTU implica una mayor cantidad de fragmentos para transmitir la misma cantidad de datos. Esto genera un aumento del número total de paquetes enviados y una sobrecarga en la red. Esta condición se confirmó al observar un mayor número de paquetes IP en Wireshark durante transmisiones con MTU reducido.

### Conclusión
El experimento permitió verificar de forma práctica cómo funciona la fragmentación en IPv4 y cómo se comportan los protocolos de transporte TCP y UDP ante la pérdida de fragmentos. Se concluye que una MTU reducida no solo causa fragmentación, sino que también incrementa el tráfico de red y puede afectar negativamente la confiabilidad en protocolos no orientados a conexión como UDP.



