from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from collections import OrderedDict
from utils.datatable_asignaciones import DataTableAsignacion	
from datetime import datetime
import hashlib
import mysql.connector
from kivy.uix.boxlayout import BoxLayout
import webbrowser
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner  

class AdminWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Builder.load_file("admin.kv")  # Carga explícita de admin.kv
        self.selected_cct_key = None
        self.mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='pos'
        )
        self.mycursor = self.mydb.cursor()

        content = self.ids.scrn_contents
        users = self.get_users("General", 0)
        userstable = DataTableAsignacion(table=users, callback=self.button_callback)  # Pasa button_callback aquí
        content.add_widget(userstable)

        #Display Products
        #product_scrn = self.ids.scrn_product_content
        #products = self.get_products()
        #prod_table = DataTableAsignacion(table=products)
        #product_scrn.add_widget(prod_table)

    def reload_users(self):
        # Obtiene el contenedor de usuarios
        content = self.ids.scrn_contents
        content.clear_widgets()

        # Obtiene nuevamente la lista de usuarios
        users = self.get_users("General", 0)

        # Crea la tabla actualizada y agrégala a la pantalla
        userstable = DataTableAsignacion(table=users, callback=self.button_callback)
        content.add_widget(userstable)

    def button_callback(self, button_text, user_id):
        if button_text == 'Ver':
            self.ver_user(user_id)

    def ver_user(self, idx):
        content = self.ids.scrn_view
        users = self.get_users("User", idx)
        user_info = {key: users[key][0] for key in users}

        content.clear_widgets()
        scroll_view = ScrollView(size_hint=(1, 1))
        user_info_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        user_info_layout.bind(minimum_height=user_info_layout.setter('height'))

        values = list(user_info.values())
        
        aspirante_text = f"Aspirante: {values[2]} {values[3]} {values[4]}"
        user_info_layout.add_widget(Label(text=aspirante_text, color=(0, 0, 0, 1), size_hint_y=None, height=50, halign='left', valign='middle'))

        conv_text = f"Aplicando a la convocatoria: {values[1]}"
        user_info_layout.add_widget(Label(text=conv_text, color=(0, 0, 0, 1), size_hint_y=None, height=50, halign='left', valign='middle'))

        aspirante_text2 = f"Fecha de nacimiento: {values[5]}"
        user_info_layout.add_widget(Label(text=aspirante_text2, color=(0, 0, 0, 1), size_hint_y=None, height=50, halign='left', valign='middle'))
        
        residencia_text = f"Residencia: {values[7]}, {values[8]}, {values[6]}"
        user_info_layout.add_widget(Label(text=residencia_text, color=(0, 0, 0, 1), size_hint_y=None, height=50, halign='left', valign='middle'))
        
        estado_text = f"Estado preferente: {values[9]}"
        user_info_layout.add_widget(Label(text=estado_text, color=(0, 0, 0, 1), size_hint_y=None, height=50, halign='left', valign='middle'))

        estado_text2 = f"en el municipio: {values[11]}"
        user_info_layout.add_widget(Label(text=estado_text2, color=(0, 0, 0, 1), size_hint_y=None, height=50, halign='left', valign='middle'))

        ciclo_text = f"Ciclo: {values[10]}"
        user_info_layout.add_widget(Label(text=ciclo_text, color=(0, 0, 0, 1), size_hint_y=None, height=50, halign='left', valign='middle'))

        # estado = values[9].replace("CONAFE ", "")
        estado = values[7]

        # Primer Spinner: Selección del CCT
        dropdown_values = self.get_dropdown_options(estado)
        spinner_cct = Spinner(
            text="Selecciona un CCT",
            values=dropdown_values,
            size_hint=(1, None),
            height=50
        )

        # Segundo Spinner: Capacitadores del CCT seleccionado
        spinner_capacitador = Spinner(
            text="Capacitador",
            values=[],  # Vacío inicialmente
            size_hint=(1, None),
            height=50
        )

        # Método para actualizar el segundo Spinner cuando cambie el primer Spinner
        def on_cct_select(spinner, text):
            claveCentro = text.split(' - ')[0]  # Obtiene solo el claveCentro del texto seleccionado
            print(claveCentro)
            self.selected_cct_key = claveCentro  # Almacena la clave en la variable
            capacitadores = self.get_capacitadores_by_cct(claveCentro)
            spinner_capacitador.values = capacitadores

        spinner_cct.bind(text=on_cct_select)

        # Añadir ambos Spinner al layout
        user_info_layout.add_widget(spinner_cct)
        user_info_layout.add_widget(spinner_capacitador)
        
        # Botón para asignar el estado del aspirante a "Asignado"
        assign_button = Button(text="Asignar Aspirante", size_hint_y=None, height=50)
        assign_button.bind(on_release=lambda x: self.assign_aspirante(values[0], spinner_capacitador.text))

        user_info_layout.add_widget(assign_button)  # Añadir el botón a la vista


        # Botón para volver a la pantalla principal
        back_button = Button(text="Regresar", size_hint_y=None, height=50)
        back_button.bind(on_release=self.go_back)

        user_info_layout.add_widget(back_button)
        scroll_view.add_widget(user_info_layout)
        content.add_widget(scroll_view)
        self.ids.scrn_mngr.current = 'scrn_view'

    def assign_aspirante(self, idx, nombreCapacitador):
        # Obtén el ID del aspirante en función del índice
        users = self.get_users("User", idx)
        aspirante_id = users['ID'][0]

        # Obtén el capacitador seleccionado del dropdown
        selected_capacitador = nombreCapacitador
        if selected_capacitador == "Capacitador":  # Verifica si no se seleccionó un capacitador
            print("Por favor, selecciona un capacitador antes de asignar.")
            return

        # Separar el nombre del capacitador para encontrar su ID en la base de datos
        capacitador_nombre = selected_capacitador.split()  # Divide el nombre completo
        nombres, apellidoPaterno, apellidoMaterno = capacitador_nombre[0], capacitador_nombre[1], capacitador_nombre[2]

        # Conectar a la base de datos
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='CONAFE'
        )
        mycursor = mydb.cursor()

        # Encuentra el id_Capacitador en base al nombre y apellidos
        sql = '''
            SELECT id_Usuario FROM Usuario
            JOIN Aspirante ON Usuario.id_Usuario = Aspirante.id_Aspirante
            WHERE Aspirante.nombres = %s AND Aspirante.apellidoPaterno = %s AND Aspirante.apellidoMaterno = %s
        '''
        mycursor.execute(sql, (nombres, apellidoPaterno, apellidoMaterno))
        capacitador_id_result = mycursor.fetchone()

        if not capacitador_id_result:
            print("Capacitador no encontrado en la base de datos.")
            mycursor.close()
            mydb.close()
            return

        capacitador_id = capacitador_id_result[0]

        # Verificar si el capacitador ya tiene al menos un aspirante asignado en la tabla `FII`
        sql = 'SELECT COUNT(*) FROM FII WHERE id_Capacitador = %s'
        mycursor.execute(sql, (capacitador_id,))
        count = mycursor.fetchone()[0]

        if count >= 1:
            # Mostrar un popup indicando que el capacitador ya tiene el cupo lleno
            popup = Popup(title='Capacitador lleno',
                          content=Label(text='Cupos llenos para este capacitador'),
                          size_hint=(0.6, 0.4))
            popup.open()
            mycursor.close()
            mydb.close()
            return

        # Si hay cupo disponible, procede a asignar el aspirante
        sql = 'UPDATE Aspirante SET estado_solicitud = %s WHERE id_Aspirante = %s'
        mycursor.execute(sql, ("Asignado", aspirante_id))

        # Inserta en la tabla FII
        sql = '''
            INSERT INTO FII (id_Capacitador, id_Aspirante, id_CCT, estadoCapacitacion, fechaInicio, fechaFinalizacion, observaciones)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        '''
        fecha_inicio = datetime.now().date()
        fecha_finalizacion = datetime.now().date()  # Puede especificar la fecha finalización si es necesaria, o dejarla nula
        observaciones = "Observación inicial"  # Cambiar o eliminar si no es necesaria

        mycursor.execute(sql, (capacitador_id, aspirante_id, self.selected_cct_key, "En inicio", fecha_inicio, fecha_finalizacion, observaciones))

        mydb.commit()

        # Cerrar la conexión a la base de datos
        mycursor.close()
        mydb.close()

        # Confirmación visual
        print(f"Aspirante con ID {aspirante_id} ha sido asignado al capacitador con ID {capacitador_id} en la tabla FII.")

        # Cambiar de pantalla a 'Manage Users' y recargar la lista de usuarios
        self.ids.scrn_mngr.current = 'scrn_content'
        self.reload_users()  # Recarga la lista de usuarios actualizada

    def get_dropdown_options(self, estado):
        # Conecta a la base de datos y obtiene las opciones
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='CONAFE'
        )
        mycursor = mydb.cursor()
        
        # Ejecuta el query para obtener claveCentro, nombre y municipio
        sql = 'SELECT claveCentro, nombre, municipio, localidad FROM CCT WHERE CCT.estado = %s'
        mycursor.execute(sql, (estado,))
        result = mycursor.fetchall()
        
        # Formatea los resultados para mostrarlos en el dropdown
        options = [f"{claveCentro} - {nombre}, {municipio}, {localidad},  " for claveCentro, nombre, municipio, localidad in result]
        
        mycursor.close()
        mydb.close()
        
        return options

    def get_capacitadores_by_cct(self, claveCentro):
        # Conectar a la base de datos y obtener capacitadores para el CCT seleccionado
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='CONAFE'
        )
        mycursor = mydb.cursor()

        # Consulta para obtener nombres de capacitadores asignados a un CCT específico
        sql = '''
            SELECT Aspirante.nombres, Aspirante.apellidoPaterno, Aspirante.apellidoMaterno 
            FROM CentroEducador
            JOIN LEC ON CentroEducador.id_LEC = LEC.id_Usuario
            JOIN Usuario ON LEC.id_Usuario = Usuario.id_Usuario
            JOIN Aspirante ON Usuario.id_Usuario = Aspirante.id_Aspirante
            WHERE CentroEducador.claveCentro = %s AND Usuario.acceso = 'Capacitador'
        '''
        mycursor.execute(sql, (claveCentro,))
        result = mycursor.fetchall()

        # Formatear resultados para mostrarlos en el dropdown
        capacitadores = [f"{nombres} {apellidoPaterno} {apellidoMaterno}" for nombres, apellidoPaterno, apellidoMaterno in result]

        mycursor.close()
        mydb.close()

        return capacitadores




    def ver_documento(self, url):
        # Lógica para abrir el documento específico
        if url:  # Asegúrate de que el URL no esté vacío
            webbrowser.open(url)
        else:
            print("URL no disponible para este documento")

    def go_back(self, instance):
        self.ids.scrn_mngr.current = 'scrn_content'


    

    def get_users(self, mode, id):
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='CONAFE'
        )
        mycursor = mydb.cursor()

        if mode == "General":
            _users = OrderedDict()
            _users['ID'] = {}
            _users['first_names'] = {}
            _users['last_names'] = {}
            _users['user_names'] = {}
            ids = []
            first_names = []
            last_names = []
            user_names = []

            sql = 'SELECT * FROM Aspirante WHERE estado_solicitud = %s'
            mycursor.execute(sql, ("Aceptado",))

            users = mycursor.fetchall()
            for user in users:
                ids.append(user[0])
                first_names.append(user[7])
                last_names.append(user[8])
                user_names.append(user[9])
            # print(designations)
            users_length = len(first_names)
            idx = 0
            while idx < users_length:
                _users['ID'][idx] = ids[idx]
                _users['first_names'][idx] = first_names[idx]
                _users['last_names'][idx] = last_names[idx]
                _users['user_names'][idx] = user_names[idx]

                idx += 1
            
            return _users
        else:
            # Lista de claves
            keys = [
                'ID', 'Convocatoria', 'nombres', 'apellidoPat', 'apellidoMat', 'Fecha Nacimiento',
                'Codigo Postal', 'Estado', 'Municipio',
                'Estado Preferente', 'Ciclo', 'Municipio Deseado'
            ]

            # Crear OrderedDict usando una comprensión

            _users = OrderedDict((key, {}) for key in keys)

            sql = 'SELECT * FROM Aspirante WHERE id_Aspirante = %s'
            mycursor.execute(sql, (id,))

            users = mycursor.fetchall()
            idx = 0

            sql = 'SELECT nombre_convocatoria FROM ConvocatoriaActual WHERE id_Convo = %s'
            mycursor.execute(sql, (users[0][1],))
            conv = mycursor.fetchall()

            for user in users:
                _users['ID'][idx] = user[0]
                _users['Convocatoria'][idx] = conv[0][0]
                _users['nombres'][idx] = user[7]
                _users['apellidoPat'][idx] = user[8]
                _users['apellidoMat'][idx] = user[9]
                _users['Fecha Nacimiento'][idx] = user[10]
            
            
            sql = 'SELECT * FROM ResidenciaAspirante WHERE id_Aspirante = %s'
            mycursor.execute(sql, (id,))

            users = mycursor.fetchall()

            for user in users:
                _users['Codigo Postal'][idx] = user[1]
                _users['Estado'][idx] = user[2]
                _users['Municipio'][idx] = user[3]
            
            sql = 'SELECT * FROM ParticipacionAspirante WHERE id_Aspirante = %s'
            mycursor.execute(sql, (id,))

            users = mycursor.fetchall()

            for user in users:
                _users['Estado Preferente'][idx] = user[1]
                _users['Ciclo'][idx] = user[2]
                _users['Municipio Deseado'][idx] = user[4]

            return _users

    def get_products(self):
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='pos'
        )
        mycursor = mydb.cursor()
        _stocks = OrderedDict()
        _stocks['product_code'] = {}
        _stocks['product_name'] = {}
        _stocks['product_weight'] = {}
        _stocks['in_stock'] = {}
        _stocks['sold'] = {}
        _stocks['order'] = {}
        _stocks['last_purchase'] = {}

        product_code = []
        product_name = []
        product_weight = []
        in_stock = []
        sold = []
        order = []
        last_purchase = []
        sql = 'SELECT * FROM stocks'
        mycursor.execute(sql)
        products = mycursor.fetchall()
        for product in products:
            product_code.append(product[1])
            name = product[2]
            if len(name) > 10:
                name = name[:10] + '...'
            product_name.append(name)
            product_weight.append(product[3])
            in_stock.append(product[5])
            sold.append(product[6])
            order.append(product[7])
            last_purchase.append(product[8])
        # print(designations)
        products_length = len(product_code)
        idx = 0
        while idx < products_length:
            _stocks['product_code'][idx] = product_code[idx]
            _stocks['product_name'][idx] = product_name[idx]
            _stocks['product_weight'][idx] = product_weight[idx]
            _stocks['in_stock'][idx] = in_stock[idx]
            _stocks['sold'][idx] = sold[idx]
            _stocks['order'][idx] = order[idx]
            _stocks['last_purchase'][idx] = last_purchase[idx]
           

            idx += 1
        
        return _stocks
        
    def change_screen(self, instance):
        if instance.text == 'Manage Products':
            self.ids.scrn_mngr.current = 'scrn_product_content'
        elif instance.text == 'Manage Users':
            self.ids.scrn_mngr.current = 'scrn_content'
        else:
            self.ids.scrn_mngr.current = 'scrn_view' 


class AdminApp(App):
    def build(self):

        return AdminWindow()

if __name__=='__main__':
    AdminApp().run()