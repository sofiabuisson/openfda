#Importamos las librerias que nos haran falta mas adelante:
import socketserver
import http.server
import http.client
import json

PORT = 8000

#Clase con nuestro manejador. Es una clase derivada de BaseHTTPRequestHandler
# Esto significa que "hereda" todos los metodos de esta clase. Y los que
# nosotros consideremos los podemos reemplazar por los nuestros
class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    # Creamos los parámetros de configuración
    SERVER_NAME = "api.fda.gov"
    RESOURCE_NAME = "/drug/label.json"
    DRUG_openfda = '&search=active_ingredient:'
    COMPANY_openfda = '&search=openfda.manufacturer_name:'

    #Creamos una funcion que nos devuelva la pagina de inicio del formulario
    def pincio(self):

        f=open("formulariosofia.html", "r") #Abrimos y leemos el formulario
        message=f.read()

        return message


    #Creamos otra funcion para almacenar los elementos introducidos en el formulario
    def inputs_html(self, lista):

        datos_html = """ """

        for i in lista:  # Iteramos sobre los elementos obtenidos, y los almacenamos
            datos_html += "<li>" + i + "</li>"
        datos_html += """
                                        </ul>
                                    </body>
                                </html>
                            """
        return datos_html


    #Creamos unna funcion que se conecta con fda y nos devuelve los resultados de la conexion
    def results(self, limit=10):

        conn = http.client.HTTPSConnection(self.SERVER_NAME)  # Establecemos conexion
        conn.request("GET", self.RESOURCE_NAME + "?limit=" + str(limit))  #Enviamos la solicitud

        print(self.RESOURCE_NAME + "?limit=" + str(limit))

        #Obtenemos la respuesta, y la transformamos en una cadena
        r1 = conn.getresponse()
        leer_json = r1.read().decode("utf8")
        data = json.loads(leer_json)

        results = data['results']

        #Esta funcion nos devuelve los resultados de la conexion
        return results


# GET. Este metodo se invoca automaticamente cada vez que hay una
# peticion GET por HTTP. El recurso que nos solicitan se encuentra
# en self.path
    def do_GET(self):

        #Dividimos el path en una lista, cuya separacion es el signo ?
        division_lista = self.path.split("?")

        #Si hay mas de 1 elemento en la lista, los parametros seran el segundo elemento de la lista
        if len(division_lista) > 1:
            parametros = division_lista[1]

        else:
            parametros = ""

        #Asignamos los valores por defecto de los parametros
        limit = 1

        #Dividimos el parametro que habíamos obtenido anteriormente
        if parametros:

            print ("Hay parametros")
            division_parametro = parametros.split("=")

            if division_parametro[0] == "limit":
                limit = int(division_parametro[1])
                print("Limit: {}".format(limit))

        else:

            print("No hay parámetros")

#-----------------------------------------------------------------------------------------------------------------------------------------------
        #No habremos introducido ningun dato, con lo cual, pedimos que nos devuelva el formulario para rellenarlo.
        if self.path == '/':

            self.send_response(200)  # Envia respuesta con el estado
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            formulario_html = self.pincio() #Nos devuelve el formulario
            self.wfile.write(bytes(formulario_html, "utf8"))


        #Este es el caso en el que buscamos la lista de medicamentos
        elif 'listDrugs' in self.path:

            self.send_response(200) #De nuevo envia la respuesta
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            drugs = []  #Creamos una lista vacia en la que incluiremos los farmacos
            results = self.results(limit)

            for resultado in results:

                if ('generic_name' in resultado['openfda']):  #En el caso en que conozcamos el nombre del medicamento
                    drugs.append(resultado['openfda']['generic_name'][0])   #Añadimos los farmacos a la lista vacia

                else:   #En el caso en que no conozcamos el nombre del medicamento
                    drugs.append('Desconocido')

            #Utilizamos la funcion creada antes para obtener la informacion que introducimos en el html
            html_devuelve = self.inputs_html(drugs)

            #Envia la informacion del html
            self.wfile.write(bytes(html_devuelve, "utf8"))

#-----------------------------------------------------------------------------------------------------------------------------------------------

        #Este es el caso en el que buscamos la lista de las empresas
        elif 'listCompanies' in self.path:

            self.send_response(200) #De nuevo envia la respuesta
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            empresas = []   #Al igual que antes, creamos una lista vacia en la que introducimos las empresas
            results = self.results(limit)

            for resultado in results:

                if ('manufacturer_name' in resultado['openfda']):   #En el caso en el que conozcamos el nombre del fabricante
                    empresas.append(resultado['openfda']['manufacturer_name'][0])   #Lo añadimos a la lista

                else:   #En el caso en el qeu no conozcamos el nombre de las empresas
                    empresas.append('Desconocido')

            #Utilizamos la funcion creada antes para obtener la informacion que introducimos en el html
            html_devuelve = self.inputs_html(empresas)

            #Envia la informacion del html
            self.wfile.write(bytes(html_devuelve, "utf8"))

#-----------------------------------------------------------------------------------------------------------------------------------------------

        #En el caso que busquemos un medicamento en concreto
        elif 'searchDrug' in self.path:

            self.send_response(200) #De nuevo, envia la respuesta
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # Establecemos los parametros por defecto
            limit = 10

            #Dividimos el path entre el nombre del parametro y el valor del mismo, y nos quedamos con el nombre del farmaco
            farmaco = self.path.split('=')[1]

            medicamentos = []   #Creamos una lista vacia donde almacenaremos la informacion del farmaco

            conn = http.client.HTTPSConnection(self.SERVER_NAME)  # Establecemos conexion con el servidor
            conn.request("GET", self.RESOURCE_NAME + "?limit=" + str(limit) + self.DRUG_openfda + farmaco)

            r1 = conn.getresponse() #Obtenemos la respuesta del servidor
            datos1 = r1.read()  #La leemos
            dato = datos1.decode("utf8")
            biblioteca_datos = json.loads(dato)
            events_search_drug = biblioteca_datos['results']

            for resultado in events_search_drug:
                if ('generic_name' in resultado['openfda']):
                    medicamentos.append(resultado['openfda']['generic_name'][0])    #Añadimos la informacion a la lista
                else:
                    medicamentos.append('Desconocido')

            #Utilizamos la funcion creada antes para obtener la informacion que introducimos en el html
            html_devuelve = self.inputs_html(medicamentos)

            #Envia la informacino del html
            self.wfile.write(bytes(html_devuelve, "utf8"))

#-----------------------------------------------------------------------------------------------------------------------------------------------

        #En el caso que busquemos una empresa en concreto
        elif 'searchCompany' in self.path:

            self.send_response(200) #Mandamos la respuesta
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            #Establecemos los parametros por defecto
            limit = 10

            #Dividimos el path entre el nombre del parametro y el valor del mismo, y nos quedamos con el nombre de la empresa
            empresa = self.path.split('=')[1]

            empresas = []   #Creamos una lista vacia donde almacenaremos la informacion de la empresa

            conn = http.client.HTTPSConnection(self.SERVER_NAME)    #Establecemos la conexion con el servidor
            conn.request("GET", self.RESOURCE_NAME + "?limit=" + str(limit) + self.COMPANY_openfda + empresa)

            r1 = conn.getresponse() #Obtenemos la respuesta
            dato1 = r1.read()   #La leemos
            dato = dato1.decode("utf8")
            biblioteca_empresa = json.loads(dato)
            find_empresa = biblioteca_empresa['results']

            for search in find_empresa:
                empresas.append(search['openfda']['manufacturer_name'][0])  #Añadimos informacion de la lista que habiamos creado

            #Utilizamos la funcion creada antes para obtener la informacion que introducimos en el html
            html_devuelve = self.inputs_html(empresas)

            #Envia la informacion del html
            self.wfile.write(bytes(html_devuelve, "utf8"))

#-----------------------------------------------------------------------------------------------------------------------------------------------

        #En el caso de que escojamos la opcion de las advertencias
        elif 'listWarnings' in self.path:

            self.send_response(200) #De nuevo envia la respuesta
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            warnings = []   #Creamos una lista vacia, al igual que anteriormente, para almacenar las advertencias
            results = self.results(limit)

            for resultado in results:  # introducimos nuestros resultados en una lista

                if ('warnings' in resultado):
                    warnings.append(resultado['warnings'][0])   #Añadimos a la lista las advertencias

                else:
                    warnings.append('Desconocido')

            #Utilizamos la funcion creada antes para obtener la informacion que introducimos en el html
            html_devuelve = self.inputs_html(warnings)

            #Envia la informacion del html
            self.wfile.write(bytes(html_devuelve, "utf8"))

#__________________________________________________________________________________________________________________________________________


        elif 'redirect' in self.path: #En este caso, queremos redirigir al cliente a la pagina principal
            print('Volvemos a la pagina principal')
            self.send_response(301) #Redirigimos a la pagina principal
            self.send_header('Location', 'http://localhost:' + str(PORT))
            self.end_headers()

        elif 'secret' in self.path:
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm="Mi servidor"')
            self.end_headers()

        else:  #En el caso que el recurso solicitado no se encuentre en el servidor, mandamos un error con el codigo 404
            print ("El recurso solicitado no se encuentra en el servidor")
            self.send_error(404) #Mandamos el error
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write("ERROR 404, NOT FOUND '{}'.".format(self.path).encode())
        return

socketserver.TCPServer.allow_reuse_address = True  # reutilizamos el puerto sin necesidad de cambiarlo
Handler = testHTTPRequestHandler
httpd = socketserver.TCPServer(("", PORT), Handler)
print("serving at port", PORT)

httpd.serve_forever()
