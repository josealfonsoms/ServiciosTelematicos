 _______________________________________________________________________________________________________________ 
|     # PUERTOS USADOS EN LIQUORSTORE            |           # PUERTOS USADOS EN BANK                           |
|  # CLIENTES      |   # COMUNICACION CON BANK   |  # CLIENTES          | # COMUNICACION CON LIQUORSTORE        |
| 8000   # TCP     |       4000   # UDP          | 9000   # TCP         |          4000   # UDP                 |
|                  |       3459   # UDP          |                      |          3459   # UDP                 |
|__________________|_____________________________|______________________|_______________________________________|

Los servidores liquorstore.py y bank.py tienen sus respectivos Dockerfile y es necesario para el correcto
funcionamiento seguir los siguientes pasos:

    1. La red docker donde estaran los contenedores desplegados
        docker network create --subnet=192.168.46.0/24 mi-red

    2. Construir las imagenes a partir del Dockerfile en cada carpeta que contienen los servidores.
        docker build -t liquorstore .
        docker build -t bank .
    
    3. Lanzar los contenedores liquorstore y bank a partir de sus imagenes construidas, en la red creada
    anteriormente mi-red, que son los contenedores llamados en las direcciones del los .py
        docker run --name liquorstore -d liquorstore
        docker run --name bank -d bank
    
    4. Desde una terminal
        telnet 192.168.46.2 8000    (Atiende el servicio de LIQUORSTORE via TCP)
        telnet 192.168.46.3 9000    (Atiende el servicio de BANK via TCP)


    
    

        