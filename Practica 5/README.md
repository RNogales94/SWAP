# Practica 5 - SWAP
##### Rafael Nogales Vaquero

## Replicación de bases de datos
#### Introducción:
A la hora de hacer copias de seguridad de nuestras bases de datos (BD) MySQL, una opción muy común suele ser la de usar una réplica maestro-esclavo, de manera que nuestro servidor en producción hace de maestro y otro servidor de backup hace de esclavo.  
Podemos hacer copias desde el servidor de backup sin que se vea afectado el rendimiento del sistema en producción y sin interrupciones de servicio.  
Tener una réplica en otro servidor también añade fiabilidad ante fallos totales del sistema en producción, los cuales, tarde o temprano, ocurrirán. Por ejemplo, podemos tener un pequeño servidor actuando como backup en nuestra oficina sincronizado mediante réplicas con nuestro sistema en producción.  
Esta opción, además, añade fiabilidad ante posibles interrupciones de servicio permanentes del servidor maestro por cualquier escenario catastrófico que nos podamos imaginar. En ese caso, tendremos posiblemente decenas de clientes y servicios parados sin posibilidad de recuperar sus datos si no hemos preparado un buen plan de contingencias. Tener un servidor de backup con MySQL actuando como esclavo de replicación es una solución asequible y no consume demasiado ancho de banda en un sitio web de tráfico normal, además de que no afecta al rendimiento del maestro en el sistema en producción.  

Los objetivos concretos de esta práctica son:  
+ Copiar archivos de copia de seguridad mediante ssh.
+ Clonar manualmente BD entre máquinas.
+ Configurar la estructura maestro-esclavo entre dos máquinas para realizar el
clonado automático de la información.
#### Entorno:

Para esta guía vamos a tener tres máquinas Ubuntu 16.04 con las siguientes carácterisiticas:

###### M1:
- IP: 192.168.1.56
- Username: user
- LAMP server

###### M2:
- IP: 192.168.1.55
- Username: user
- LAMP server


### Crear una base de datos en MySQL:

Para el resto de la práctica debemos crearnos una BD en MySQL e insertar algunos datos. Así tendremos datos con los cuales hacer las copias de seguridad. En todo momento usaremos la interfaz de línea de comandos del MySQL:  

Nos conectamos a mysql con:

```
mysql -u root -p
```

*Nota si escribimos -uroot -p"pass" (sin espacios) no nos pide la contraseña en el siguiente paso, esto es util en algunos scripts*

Comandos (y su salida) para la inicialización de la BD:


```
mysql> SHOW DATABASES;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| sys                |
+--------------------+
4 rows in set (0,01 sec)

mysql> CREATE DATABASE contactos;
Query OK, 1 row affected (0,00 sec)

mysql> USE contactos;
Database changed
mysql> SHOW TABLES;
Empty set (0,00 sec)

mysql> CREATE TABLE datos(nombre varchar(100), tlf int);
Query OK, 0 rows affected (0,03 sec)

mysql> SHOW TABLES;
+---------------------+
| Tables_in_contactos |
+---------------------+
| datos               |
+---------------------+
1 row in set (0,00 sec)

mysql> INSERT INTO datos(nombre, tlf) VALUES ("pepe", 95834987);
Query OK, 1 row affected (0,06 sec)

mysql> SELECT * FROM datos;
+--------+----------+
| nombre | tlf      |
+--------+----------+
| pepe   | 95834987 |
+--------+----------+
1 row in set (0,00 sec)

mysql> DESCRIBE datos;
+--------+--------------+------+-----+---------+-------+
| Field  | Type         | Null | Key | Default | Extra |
+--------+--------------+------+-----+---------+-------+
| nombre | varchar(100) | YES  |     | NULL    |       |
| tlf    | int(11)      | YES  |     | NULL    |       |
+--------+--------------+------+-----+---------+-------+
2 rows in set (0,00 sec)

mysql> quit
Bye

```



#### Replicar una BD MySQL con mysqldump

MySQL ofrece la una herramienta para clonar las BD que tenemos en nuestra maquina. Esta herramienta es mysqldump.

mysqldump es parte de los programas de cliente de MySQL, que puede ser utilizado para generar copias de seguridad de BD. Puede utilizarse para volcar una o varias BD para copia de seguridad o para transferir datos a otro servidor SQL (no necesariamente un servidor MySQL). EL volcado contiene comandos SQL para crear la BD, las tablas y rellenarlas.

Esta herramienta soporta una cantidad considerable de opciones. Ejecuta como root el siguiente comando:

```
mysqldump --help
```
para obtener la lista completa. En la siguiente URL se explican con detalle todas las opciones posibles:
[Referencias](http://dev.mysql.com/doc/refman/5.0/es/mysqldump.html)

Concretamente, las opciones --quick o --opt hacen que MySQL cargue el resultado entero en memoria antes de volcarlo a fichero, lo que puede ser un problema si se trata de una BD grande. Sin embargo, la opción --opt está activada por defecto.

La sintaxis de uso es:
```
mysqldump contactos -u root -p > /root/contactos.sql
```


Esto puede ser suficiente, pero tenemos que tener en cuenta que los datos pueden estar actualizándose constantemente en el servidor de BD principal. En este caso, antes de hacer la copia de seguridad en el archivo .SQL debemos evitar que se acceda a la BD para cambiar nada.
Así, en el servidor de BD principal (maquina1) hacemos:
```
mysql -u root –p
mysql> FLUSH TABLES WITH READ LOCK;
mysql> quit
```
Ahora ya sí podemos hacer el mysqldump para guardar los datos. En el servidor principal (maquina1) hacemos:
```
mysqldump contactos -u root -p > /tmp/contactos.sql
```
Como habíamos bloqueado las tablas, debemos desbloquearlas (quitar el “LOCK”):
```
mysql -u root –p
mysql> UNLOCK TABLES; mysql> quit
```

Ya podemos ir a la máquina esclavo (maquina2, secundaria) para copiar el archivo .SQL con todos los datos salvados desde la máquina principal (maquina1):  
```
scp maquina1:/tmp/contactos.sql /tmp/
```
En mi caso:
```
scp 192.168.1.44:/tmp/contactos.sql /tmp/
```
y habremos copiado desde la máquina principal (1) a la máquina secundaria (2) los datos que hay almacenados en la BD.  

Es importante destacar que el archivo .SQL de copia de seguridad tiene formato de texto plano, e incluye las sentencias SQL para restaurar los datos contenidos en la BD en otra máquina. Sin embargo, la orden mysqldump no incluye en ese archivo la sentencia para crear la BD (es necesario que nosotros la creemos en la máquina secundaria en un primer paso, antes de restaurar las tablas de esa BD y los datos contenidos en éstas).  

Con el archivo de copia de seguridad en el esclavo ya podemos importar la BD completa en el MySQL. Para ello, en un primer paso creamos la BD:  

```
mysql -u root –p
mysql> CREATE DATABASE contactos;
mysql> quit
```
Y en un segundo paso restauramos los datos contenidos en la BD (se crearán las tablas en el proceso):
```
mysql -u root -p contactos < /tmp/contactos.sql
```

Por supuesto, también podemos hacer la orden directamente usando un “pipe” a un ssh para exportar los datos al mismo tiempo (siempre y cuando en la máquina secundaria ya hubiéramos creado la BD):
```
mysqldump ejemplodb -u root -p | ssh equipodestino mysql
```

#### Replicación de BD mediante una configuración maestro-esclavo

La opción anterior funciona perfectamente, pero es algo que debe realizar un operador a mano. Sin embargo, MySQL tiene la opción de configurar el demonio para hacer replicación de las BD sobre un esclavo a partir de los datos que almacena el maestro.  
Se trata de un proceso automático que resulta muy adecuado en un entorno de producción real. Implica realizar algunas configuraciones, tanto en el servidor principal como en el secundario.  
A continuación se detalla el proceso a realizar en ambas máquinas, para lo cual, supondremos que partimos teniendo clonadas las base de datos en ambas máquinas (como lo hemos dejado antes).

Lo primero que debemos hacer es la configuración de mysql del maestro. Para ello editamos, como root, el */etc/mysql/my.cnf* (aunque según la versión de mysql puede que la configuración esté en el archivo */etc/mysql/mysql.conf.d/mysqld.cnf*) para realizar las modificaciones que se describen a continuación.

Comentamos el parámetro bind-address que sirve para que escuche a un servidor:  
```
#bind-address 127.0.0.1
```

Le indicamos el archivo donde almacenar el log de errores. De esta forma, si por
ejemplo al reiniciar el servicio cometemos algún error en el archivo de configuración,
en el archivo de log nos mostrará con detalle lo sucedido:
```
log_error = /var/log/mysql/error.log
```

Establecemos el identificador del servidor.
```
server-id = 1
```
El registro binario contiene toda la información que está disponible en el registro de actualizaciones, en un formato más eficiente y de una manera que es segura para las transacciones:
```
log_bin = /var/log/mysql/bin.log
```
Guardamos el documento y reiniciamos el servicio:
```
/etc/init.d/mysql restart
```

Si no nos ha dado ningún error la configuración del maestro, podemos pasar a hacer la configuración del mysql del esclavo (editar como root su archivo de configuración).

La configuración es similar a la del maestro, con la diferencia de que el server-id en esta ocasión será 2. Si trabajamos en versiones de mysql 5.5 o superiores (será lo habitual si la versión de Linux es actual), los datos de configuración para indicar cuál es la máquina maestra se deben añadir desde el servicio mysql (según veremos un poco más adelante).

##### MySQL >= 5.5
El primer paso es editar el archivo */etc/mysql/mysql.conf.d/mysqld.cnf*
en la máquina esclavo con la siguiente configuración:

```
mysql> CREATE USER esclavo IDENTIFIED BY 'esclavo';
mysql> GRANT REPLICATION SLAVE ON *.* TO 'esclavo'@'%' IDENTIFIED BY 'esclavo';
mysql> FLUSH PRIVILEGES;
mysql> FLUSH TABLES;
mysql> FLUSH TABLES WITH READ LOCK;
```



```
bind-address = <IP_MASTER>
server-id = 2
log-bin = /var/log/mysql/mysql-bin.log
```
Reiniciamos la BD para recargar los archivos de configuración que acabamos de cambiar.
```
sudo service mysql restart
```

Establecemos la dependencia a la mysql master.  

Volvemos a la máquina master y ejecutamos lo siguiente:
```
SHOW MASTER STATUS;
```
Nos devolverá un resultado similar a este:
```
+------------------+----------+--------------+------------------+-------------------+
| File             | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set |
+------------------+----------+--------------+------------------+-------------------+
| mysql-bin.000004 |     1564 |              |                  |                   |
+------------------+----------+--------------+------------------+-------------------+
1 row in set (0,00 sec)
```

Es importante el número *Position* ya que debemos indicarselo a la BD esclava:

```
mysql> CHANGE MASTER TO MASTER_HOST='192.168.1.44',
        MASTER_USER='esclavo',
        MASTER_PASSWORD='esclavo',
        MASTER_LOG_FILE='mysql-bin.000004',
        MASTER_LOG_POS=1564,
        MASTER_PORT=3306;

mysql> START SLAVE;

```

Ahora volvemos a la base de datos master:
```
mysql> UNLOCK TABLES;
```
Con esto ya debería funcionar, podemos probar a crear tuplas en la BD maestra
y ver como se insertan también en la esclavo.
### Comprobaciones:
Podemos ejecutar la siguiente sentencia en la BD esclavo
```
mysql> SHOW SLAVE STATUS\G
```
Y si *Seconds_Behind_Master* no es "null" significa que la BD se está sincronizando
correctamente.
