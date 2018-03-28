# Practica 3 - SWAP
##### Rafael Nogales Vaquero

## Balanceo de Carga
#### Introducción:
En esta práctica configuraremos una red entre varias máquinas de forma que tengamos un balanceador que reparta la carga entre varios servidores finales.  
El problema a solucionar es la sobrecarga de los servidores. Se puede balancear cualquier protocolo, pero dado que esta asignatura se centra en las tecnologías web, balancearemos los servidores HTTP que tenemos configurados.  
De esta forma conseguiremos una infraestructura redundante y de alta disponibilidad.  

*Se podría considerar una solución basada en balanceo por DNS pero tiene el problema de que si una máquina muere el servidor DNS no puede enterarse de esto y seguirá redirigiendo tráfico hacia la máquina muerta, por tanto una parte de los usuarios verían nuestra página caida hasta que caduque la caché del navegador del usuario (o hasta que la borre, pero eso no es una solución aceptable ni conseguiremos alta disponibilidad).*

El primer paso "Paso 0" es instalar una nueva máquina *Balancador* a nuestro entorno.  
Esta máquina en mi caso es otro Ubuntu 16.04 al que le hemos configurado un servidor ssh para poder controlarla desde remoto y sin ningún otro añadido.  
Durante la práctica vamos a probar dos configuraciones distintas para esta máquina:
 + Opción 1: Usar NGINX
 + Opción 2: Usar HAProxy   

#### Entorno:

Para esta guía vamos a tener tres máquinas Ubuntu 16.04 con las siguientes carácterisiticas:

###### M1:
- IP: 192.168.1.36
- Username: user
- LAMP server

###### M2:
- IP: 192.168.1.64
- Username: user
- LAMP server

###### Balanceador:
- IP: 192.169.1.59
- Username: user


### Opción 1: Usar NGINX como balanceador de carga:

#### Acerca de NGINX:
*nginx* (pronunciado en inglés “engine X”) es un servidor web ligero de alto rendimiento. Lo usan muchos sitios web conocidos, como: WordPress, Hulu, GitHub, Ohloh, SourceForge, TorrentReactor y partes de Facebook. Su página principal (en español) es http://wiki.nginx.org/NginxEs  

Debido a su buen rendimiento, también se usa como servidor web en lugar del Apache o IIS, aunque uno de los usos más extendidos es como balanceador de carga en un cluster web. De esta forma, el servidor con la IP pública (de cara a Internet) ejecuta el nginx, que se ocupa de redirigir el tráfico a los servidores finales.  
Estos servidores finales pueden servir su contenido web con cualquier servidor, no necesariamente deben ser nginx tambien.

**Nota:** *nginx* es especialmente bueno cuando se trata de servir contenido estático.

#### Paso 1: Instalación de nginx

##### Actualización inicial
Como siempre que trabajamos en una máquina recién instalada conviene actualizar sus paquetes, para ello podemos usar esta orden resumida:
```
sudo apt-get update && sudo apt-get dist-upgrade && sudo apt-get autoremove
```

O bien hacer el típico:
```
sudo apt-get update
sudo apt-get upgrade
```
##### Instalar nginx:
Para instalar *nginx* de nuevo usamos el típico apt-get:
```
sudo apt-get install nginx
```
nginx es un servidor muy ligero por lo que la duración de la instalación será especialmente corta.  

Para arrancar nginx utilizamos el gestor de demonios del sistema:  
```
sudo systemctl start nginx
```

##### Comprobaciones:
Para comprobar que está funcionando podemos usar systemctl de nuevo:
```
systemctl | grep "nginx"
```
Y nos debe aparecer algo de este estilo:
```
  loaded active running  <Descripción de nginx>
```

Ampliación: [Más opciones de systemctl](https://wiki.archlinux.org/index.php/systemd_(Español)

##### Cortafuegos
Por defecto Ubuntu al instalar un servidor web lo añade a la lista blanca del cortafuegos, puedes verificarlo con el comando ufw:
```
sudo ufw app list
```

En mi caso el cortafuegos tiene las siguientes reglas:
```
Available applications:
  Nginx Full
  Nginx HTTP
  Nginx HTTPS
  OpenSSH
```
Si Nginx no apareciese en la lista del cortafuegos o si tuviesemos algún otro problema podemos consultar [la guía de instalación detallada de nginx](https://www.liberiangeek.net/2016/07/how-to-install-nginx-webserver-on-ubuntu-16-04/)

#### Paso 2: Configurar nginx como balanceador de carga


### Usar HAProxy como balanceador de carga:
#### Paso 1:
