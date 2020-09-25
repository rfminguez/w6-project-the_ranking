# The Ranking
## Introducción
Este es el proyecto de la semana 6 de IronHack y se divide en tres partes:
- Descargar todas las pull requests de un repositorio de Github.
- Analizar esas pull requests para obtener información. Los datos se guardan en una base de datos mongodb.
- Publicar una API que responda a consultas sobre la información guardada.

## Desarrollo
Se han creado dos scripts principales para hacer este trabajo:
### 1. load_pull_requests.py
Conecta a la API de github, descarga todas las pull requests de un repositorio:

Para cada pull request hace dos llamadas adicionales a la API de Github:
  * descargar los datos de comentarios.
  * descargar los datos de commits.

Una vez descargados los datos los procesa y los guarda en una base de datos mongodb.

**Importante**: dado que el número de llamadas a la API de Github es limitado podemos sobrepasarlo si un proyecto tiene muchas pull requests.
Por ejemplo, para un proyecto con 500 pull requests hace el siguiente número de llamadas:
  * 5 para descargarse las 500 pull requests (100 pull requests por 5 páginas).
  * 1000 llamadas para los comentarios (1 por cada pull request).
  * 1000 llamadas para los commits (ídem).
  
### 2. server.py 
Usando *Flask* publica una API en el puerto 3000 del ordenador local que responde a peticiones para extraer la información guardada.

### Scripts adicionales
Para facilitar el mantenimiento, el código se ha separado en varios ficheros:
#### src/app.py 

Setup de Flask para publicar la API.
#### src/config.py

Extrae parámetros de entorno con la librería *dotenv*: el puerto donde escucha la API, el token de autenticación de la API y la URL de conexión a la base de datos entre otros.
#### src/database.py 

Setup de la conexión a la base de datos mongodb con la librería *pymongo*.
#### src/controllers/students_controllers.py

Código para los endpoints:
  * /student/create/\<studentname\>
  * /student/all

#### src/controllers/labs_controllers.py

Código para los endpoints:
  * /lab/create
  * /lab/<lab_id>/search
  * /lab/memeranking
  * /lab/<lab_id>/meme

## Instrucciones
### .env
La configuración de los componentes del proyecto se hace mediante variables de entorno.

Para esto necesitamos un fichero ```.env``` en el directorio donde están los dos scripts principales con las siguienges variables:
- **PORT** el puerto en que escucha nuestra API.
- **DB_URL** la url de conexión a la base de datos mongodb.
- **GITHUB_APIKEY** el token de autenticación para conectar con la API de Github.

### mongodb
Para guardar y consultar la información se necesita una base de datos mongodb. Como es un proyecto para un bootcamp estoy utilizando una base de datos en local que escucha al puerto 27017.

Esto es configurable en el fichero ```.env``` mediante la variable de entorno ```DB_URL```. 
### load_pull_requests.py
Una vez está la base de datos funcionando podemos cargar los pull requests.

```python3 load_pull_requests.py```

Este script se conecta a la API de Github para descargar y procesar la información de pull requests. Este proceso tarda bastante (para hacernos una idea, alrededor de cinco minutos para un repositorio con 500 pull requests).

Los datos se guardan en el mongodb que hemos configurado en ```.env```. Para acceder a la API de Github usamos un token de autenticación que debe estar en la variable de entorno ```GITHUB_APIKEY```.
### server.py
Cuando tenemos los datos podemos levantar nuestra API lanzando ejecutando este script.

```python3 server.py```

Escucha en el puerto que le indiquemos en la variable ```PORT```del fichero ```.env```.

Atiende a los siguientes endpoints:
#### /student/create/\<studentname\>

Método GET.

Recibe un nombre de alumno, comprueba que el usuario no existe ya en la base de datos y que el usuario está en github. Si pasa las validaciones lo guarda en mongodb.
#### /student/all

Método GET.

Devuelve una lista de los alumnos registrados en la base de datos.
#### /lab/create

Método POST.

Recibe un JSON con el nombre de un lab, comprueba que el lab no existe en la base de datos y si supera la validación lo guarda en monbodb.
#### /lab/<lab_id>/search

Método GET.

Recibe un id de un lab, comprueba si este lab se aha registrado en la base de datos y si es así devuelve datos de:
  * número de pull requests abiertas.
  * número de pull requests cerradas.
  * porcentaje de pull requests abiertas.
  * porcentaje de pull requests cerradas.
  * lista de memes únicos usados en este lab (busca imágenes jpg, jpeg y png en el campo *body* de la pull request).
  * lista de alumnos que no han hecho pull request en este lab (busca entre los alumnos que están registrados en la base de datos).
  * tiempo medio que cada instructor tarda en corregir el lab (lo calculo restando la hora de cierre de la pull request menos la hora en que se hizo el último commit a la pull request).
  * tiempo de corrección máximo por instructor.
  * tiempo de corrección mínimo por instructor.
#### /lab/memeranking

Método GET.

Devuelve todos los proyectos y los cinco memes que más se han usado en cada proyecto.
#### /lab/<lab_id>/meme

Método GET.

Recibe un id de proyecto y devuelve un meme aleatorio de los que hay en ese proyecto.

# TO-DO

Refactorizar el código, especialmente la parte del endpoint ```/lab/<lab_id>/search``` dentro del fichero ```labs_controllers.py```.

Separar el código de los controllers de las validaciones y de acceso a bases de datos.
