Sistemas Node.js Escalables
============================

### Rafael Nogales
### UGR - SWAP

---
# Introducción:
![150%](./img/sliders/nodejs-logo.png)

---


![200%](./img/sliders/ssr-csr.png)


---
# Client side rendering (CSR)
* SPA
* Hosting barato
* Uso de CDN
* Despliegues fáciles
* Obliga a separar lógica e interfaz
* Misma UI para Web, móviles, and Escritorio.


---
# Server side rendering (SSR)

* Mejor rendimiento del SEO 
* Mejoras de prestaciones **para nuestros usuarios**

---
# Principales usos de Node.js
![](./img/sliders/nodejs-development-services-mobile-backend.jpg)

---
# Problemas de Node.js

![](./img/sliders/node-problems.png)

* Node es lento sirviendo archivos estáticos
* Node usa un solo núcleo de nuestra máquina

---
# Soluciones
* Balanceo de carga
* Servir contenido estático desde NGINX


![](./img/sliders/nginx-balancer.png)

---
# Concretamente:
**/etc/nginx/conf.d/default.conf**
``` nginx
upstream nodejs-workers {
    ip_hash;                              # Mantener sesiones             
    server 192.168.1.54:8080 weight=1;    # NodeJS instance.1      
    #server <IP o dominio> weight=1;      # NodeJS instance.2
    keepalive 10;
}
```



---
**/etc/nginx/conf.d/default.conf**

``` nginx
server{
    listen 80;
    server_name balanceador;

    access_log /var/log/nginx/balanceador.access.log;
    error_log /var/log/nginx/balanceador.error.log;

    root /var/www/html;

    location / {
        try_files $uri $uri/ @backend $uri.html =404;
    }

    location @backend {
        proxy_pass http://nodejs-workers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }
}
```


---


# Sources:

https://medium.com/walmartlabs/the-benefits-of-server-side-rendering-over-client-side-rendering-5d07ff2cefe8

https://medium.freecodecamp.org/heres-why-client-side-rendering-won-46a349fadb52

https://belitsoft.com/nodejs-development-services

https://www.stevesouders.com/blog/2012/02/10/the-performance-golden-rule/

https://iwf1.com/apache-vs-nginx-vs-node-js-and-what-it-means-about-the-performance-of-wordpress-vs-ghost