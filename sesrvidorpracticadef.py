import http.server
import http.client
import socketserver
import json

# -- Puerto donde lanzar el servidor
PORT = 8000
socketserver.TCPServer.allow_reuse_address = True
headers = {'User-Agent': 'http-client'}
class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    message="default content"

    def openfda_req(self, limit=1, search=""):

        # Crear la cadena con la peticion
        req_str = '/drug/label.json/'+'?limit={}'.format(limit)

        # Si hay que hacer busqueda, añadirla a la cadena de peticion
        if search != "":
            req_str += '&search={}'.format(search)

        print("Recurso solicitado: {}".format(req_str))

        conn = http.client.HTTPSConnection("api.fda.gov")

        # Enviar un mensaje de solicitud
        conn.request("GET", req_str, None, headers)

        # Obtener la respuesta del servidor
        r1 = conn.getresponse()


        print("  * {} {}".format(r1.status, r1.reason))

        # Leer el contenido en json, y transformarlo en una cadena
        farmac = r1.read().decode("utf-8")
        conn.close()

        # ---- Procesar el contenido JSON

        return json.loads(farmac)

    def req_pinicio(self):
        f=open("formulariofdadef.html", "r")
        message=f.read()
        return message

    def find_farmacos(self, search, limit=10):
        #Nos conectamos al servidor fda

        farmacos= self.openfda_req(limit)

        message = (' <!DOCTYPE html>\n'
                       '<html lang="es">\n'
                       '<head>\n'
                       '    <meta charset="UTF-8">\n'
                       '</head>\n'
                       '<body>\n'
                       '<p>Nombre. Marca. Fabricante.</p>'
                       '\n'
                       '<ul>\n')


        for farmaco in farmacos['results']:
            if farmaco['openfda']:
                nombre=farmaco['openfda']['substance_name'][0]
                marca=farmaco['openfda']['brand_name'][0]
                fabricante=farmaco['openfda']['manufacturer_name'][0]

            else:
                nombre="No se sabe"
                marca="No se sabe"
                fabricante="No se sabe"

            message += "<li>{}. {}. {}</li>\n".format(nombre, marca, fabricante)
        message += ('</ul>\n'
                    '\n'
                    '<a href="/">Home</a>'
                    '</body>\n'
                    '</html>')
        print ("llegando la infor..............")
        return message

    def find_empresa(self,search, limit=10):
        empresas=self.openfda_req(limit)
        message=(' <!DOCTYPE html>\n'
                       '<html lang="es">\n'
                       '<head>\n'
                       '    <meta charset="UTF-8">\n'
                       '</head>\n'
                       '<body>\n'
                       '<p>Fabricantes</p>'
                       '\n'
                       '<ul>\n')
        for empresa in empresas['results']:
            if empresa['openfda']:
                nombre_empresa=empresa['openfda']['manufacturer_name'][0]
                try:
                    message += "<li>{}</li>".format(nombre_empresa)
                except KeyError:
                    pass

        message += ('</ul>\n'
                        '\n'
                        '<a href="/">Home</a>'
                        '</body>\n'
                        '</html>')

        print ("llegando..........")
        return message


# Clase con nuestro manejador. Es una clase derivada de BaseHTTPRequestHandler
# Esto significa que "hereda" todos los metodos de esta clase. Y los que
# nosotros consideremos los podemos reemplazar por los nuestros


    # GET. Este metodo se invoca automaticamente cada vez que hay una
    # peticion GET por HTTP. El recurso que nos solicitan se encuentra
    # en self.path
    def do_GET(self):
        print("Path: ",self.path)
        message=""
        global farm
        global comp
        #Dividimos el path en dos partes: por un lado, el nombre que le hemos dado a action, y por otro, el parametro al que enviamos informacion:
        division= self.path.split("?")
        #El primer elemento de nuestra lista sera el nombre que le hemos dado a action,
        nombreaction=division[0]
        if len(division)>1:
            parametro=division[1]
        else:
            parametro=""

        print("Nombreaction: {}, parametro: {}".format(nombreaction, parametro))
        limit = 1
        if parametro:
            print ("Hay parametros")
        #Dividimos el parametro entre el nombre y el valor del mismo:
            division_parametro=parametro.split("=")
            print ("division_parametro es: ", division_parametro)
            if division_parametro[0]=='Farmaco':
                farm=division_parametro[1]
                print ("farm es...", farm)
            elif division_parametro[0]=='Nombre+de+la+empresa':
                comp=division_parametro[1]
            elif division_parametro[0]=="limit":
                limit=int(division_parametro[1])
                print("Limit: {}".format(limit))
        else:
            print ("No hay parametros")


        if nombreaction=="/":
        #No habremos introducido ningun dato, con lo cual, pedimos que nos devuelva el formulario para rellenarlo.
            message= self.req_pinicio()

        elif nombreaction=="/nombrefarmaco":
        #Estamos solicitando informacion sobre el medicamento que hemos introducido en el formulario
            message=self.find_farmacos(search='&search=active_ingredient:'+ farm)


        elif nombreaction=="/nombreempresa":
        #Estamos solicitando informacion sobre la empresa que hemos introducido en el formulario
            message = self.find_empresa(search='&search=openfda.manufacturer_name:'+ comp)


        elif nombreaction=="/listadofarmacos":
        #Estamos solicitando informacion sobre el listado de farmacos que hemos introducido en el formulario
            message=self.find_farmacos(limit=10,search="listDrugs")

        elif nombreaction=="/listadoempresas":
        #Estamos solicitando informacion sobre el listado de empresas que hemos introducido en el formulario
            message=self.find_empresa(limit=10, search="listCompanies")


        # La primera linea del mensaje de respuesta es el
        # status. Indicamos que OK
        self.send_response(200)

        # En las siguientes lineas de la respuesta colocamos las
        # cabeceras necesarias para que el cliente entienda el
        # contenido que le enviamos (que sera HTML)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Este es el mensaje que enviamos al cliente: un texto y
        # el recurso solicitado
        # Enviar el mensaje completo
        self.wfile.write(bytes(message, "utf8"))
        print("File served!")
        return

# ----------------------------------
# El servidor comienza a aqui
# ----------------------------------
# Establecemos como manejador nuestra propia clase
Handler = testHTTPRequestHandler

# -- Configurar el socket del servidor, para esperar conexiones de clientes
httpd= socketserver.TCPServer(("", PORT), Handler)
print("serving at port", PORT)

    # Entrar en el bucle principal
    # Las peticiones se atienden desde nuestro manejador
    # Cada vez que se ocurra un "GET" se invoca al metodo do_GET de
    # nuestro manejador
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("")
    print("Interrumpido por el usuario")

print ("")
print ("Servidor parado")
