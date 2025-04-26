## Como probar el codigo

- Ejecutar el servidor
```sh
python3 start_server.py -H 127.0.0.1 -p 9000 -s ./downloads
```

- Ejecutar el cliente
```sh
python3 upload.py -H 127.0.0.1 -p 9000 -s ./uploads/momo.jpeg -n copia4.jpeg
```

- stress test
```sh
python3 stress_test.py
```

## Probar con mininet

- Correr topologia
```sh
sudo python3 topo.py
```

- Luego para el server:
```sh
mininet> server python3 start_server.py -H 10.0.0.1 -p 9000 -s ./downloads &
```

- Para el cliente:
```sh
mininet> client python3 upload.py -H 10.0.0.1 -p 9000 -s ./uploads/momo.jpeg -n copia1.jpeg
```
