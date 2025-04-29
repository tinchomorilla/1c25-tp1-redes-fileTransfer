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

- Para correr el script de la topologia en mininet
```sh
sudo python3 src/lib/mininet/topology.py
```

- Ejecutar el servidor
```sh
python3 src/start_server.py -H 127.0.0.1 -p 9000 -s src/lib/Server/downloads
```

- Ejecutar el cliente
  - Upload
```sh
python3 src/upload.py -H 127.0.0.1 -p 9000 -s src/lib/Client/uploads/momo.jpeg -n copia4.jpeg -r stop_and_wait
```

- Correr tests
```sh
python3 src/tests/stress_test.py 
```

## Anexo, Fragmentación IPv4: Objetivo

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

```
h1 --- s1 --- s2 --- s3 --- h2
```

- 2 hosts (`h1`, `h2`)
- 3 switches intermedios
- MTU reducido en una interfaz de `s2`
- Pérdida de paquetes simulada en una interfaz de `s3`

---

## Instrucciones paso a paso

### Preparación del entorno
Instalar Mininet, iperf y Wireshark:
```bash
sudo apt update
sudo apt install mininet iperf wireshark
```

### 1. Ejecutar el script

```bash
sudo python3 fragmentation_topo.py
```

Este script:
- Crea la topología de red
- Aplica un MTU de 500 bytes en `s2-eth1`
- Simula pérdida de paquetes del 10% en `s3-eth1`
- Elimina el flag DF para permitir fragmentación
- Inicia `iperf -s -u` en `h2`
- Podemos ver con `wireshark> h2 netstat -lunp` que el puerto UDP es el 5001

---

### 2. Enviar y capturar tráfico

##### UDP con fragmentación
(usar tamaño mayor al MTU reducido)
```bash
mininet> h1 iperf -c h2 -u -l 1500 -t 10
```
##### TCP con fragmentación
```bash
mininet> h1 iperf -c h2 -l 1500 -t 10
```


Desde una terminal externa o Wireshark, capturá en la interfaz correspondiente (ej. `s2-eth1`).


#### Filtros recomendados en Wireshark:
- Fragmentos IP:
  ```
  ip.flags.mf == 1 || ip.frag_offset > 0
  ```
- Retransmisiones TCP:
  ```
  tcp.analysis.retransmission
  ```

- Pérdida de paquetes UDP:
  ```
wireshark /tmp/fragmentacion.pcap
```
---

## Análisis esperado

### Fragmentación IPv4
- Ver múltiples fragmentos con mismo ID
- Offsets: 0, 480, 960, etc.
- `MF = 1` en fragmentos intermedios, `MF = 0` en el último

### UDP con pérdida
- No hay retransmisión
- Faltan fragmentos en la secuencia

### TCP con pérdida (recomendado para extensión)
- Se ven retransmisiones
- Mayor latencia por reenvíos

### Aumento de tráfico con MTU bajo
- Mismo payload genera más paquetes IP

---

## Screenshots de Wireshark

Agregá aquí capturas de:
- Fragmentos IP
- Campo MF y Offset en detalle
- Pérdida de paquetes UDP
- Retransmisión TCP (si se prueba)

---

## 🔹 Conclusiones (para completar)

- Se observó claramente la fragmentación de paquetes al reducir el MTU
- Se evidenció la diferencia de comportamiento entre TCP y UDP ante pérdida de fragmentos
- El uso de Wireshark permitió identificar los fragmentos, el flag MF y los offsets
- Automatizar el experimento permitió ejecutar pruebas consistentes y reproducibles

---

## 📖 Bibliografía / herramientas

- Documentación oficial de Mininet
- RFC 791 - Internet Protocol
- `man iperf`, `man ping`
- https://wiki.wireshark.org/IPv4
