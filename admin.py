from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder
from datetime import datetime
import hashlib
import mysql.connector
import webbrowser
from collections import OrderedDict
from utils.datatable import DataTable
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView

class AdminWindow(Screen):  # Cambiamos a Screen en lugar de BoxLayout
    def __init__(self, conv, **kwargs):
        super().__init__(**kwargs)
        self.conv = conv
        Builder.load_file("admin.kv")  # Carga explícita de admin.kv
        self.mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='CONAFE'
        )
        self.mycursor = self.mydb.cursor()

        content = self.ids.scrn_contents
        users = self.get_users("General", 0, conv)
        userstable = DataTable(table=users, callback=self.button_callback)
        content.add_widget(userstable)

        #Display Products
        #product_scrn = self.ids.scrn_product_content
        #products = self.get_products()
        #prod_table = DataTable(table=products)
        #product_scrn.add_widget(prod_table)

    def reload_users(self):
        # Obtiene el contenedor de usuarios
        content = self.ids.scrn_contents
        content.clear_widgets()

        # Obtiene nuevamente la lista de usuarios
        users = self.get_users("General", 0, self.conv)

        # Crea la tabla actualizada y agrégala a la pantalla
        userstable = DataTable(table=users, callback=self.button_callback)
        content.add_widget(userstable)

    def button_callback(self, button_text, idx, user_id):
        print(user_id)
        if button_text == 'Aceptar':
            self.aceptar_user(user_id)
        elif button_text == 'Rechazar':
            self.rechazar_user(user_id)
        elif button_text == 'Ver':
            self.ver_user(user_id, self.conv)

    def aceptar_user(self, user_id):
        # Conexión a la base de datos
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='CONAFE'
        )
        mycursor = mydb.cursor()

        # Actualizar el estado en ambas tablas usando `user_id`
        update_sql = 'UPDATE Aspirante SET estado_solicitud = %s WHERE id_Aspirante = %s'
        mycursor.execute(update_sql, ("Aceptado", user_id))
        
        mydb.commit()  # Guarda los cambios

        print(f"El usuario con ID {user_id} ahora tiene acceso 'Aceptado'.")
        mycursor.close()
        self.reload_users()

    def rechazar_user(self, user_id):
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='CONAFE'
        )
        mycursor = mydb.cursor()

        update_sql = 'UPDATE Aspirante SET estado_solicitud = %s WHERE id_Aspirante = %s'
        mycursor.execute(update_sql, ("Rechazado", user_id))
        mydb.commit()  # Guarda los cambios

        print(f"El usuario con ID {user_id} ahora tiene acceso 'Rechazado'.")
        mycursor.close()
        self.reload_users()




    def ver_user(self, idx, conv):
        content = self.ids.scrn_view
        # Obtén los datos del usuario en base al índice
        users = self.get_users("User", idx, conv)
        user_info = {key: users[key][0] for key in users}

        # Limpia la pantalla de visualización de usuario
        content.clear_widgets()

        # Crea un ScrollView para que el contenido sea desplazable
        scroll_view = ScrollView(size_hint=(1, 1))
        doc_names = ["Ver Certificado", "Ver Identificacion", "Ver Edo. Cuenta"]
        doc_count = 0
        # Crea un layout para mostrar los datos del usuario
        user_info_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        user_info_layout.bind(minimum_height=user_info_layout.setter('height'))
        total_items = len(user_info)
        # Agrega botones con información del usuario
        for idx, (key, value) in enumerate(user_info.items()):
            # Si estamos en los últimos tres elementos, crea un botón para abrir el documento
            if idx >= total_items - 3:
                doc_button = Button(text=f"{doc_names[doc_count]}", size_hint_y=None, height=50)
                doc_count += 1
                # Asocia el evento `on_release` para abrir el documento correspondiente
                doc_button.bind(on_release=lambda instance, url=value: self.ver_documento(url))
                user_info_layout.add_widget(doc_button)
            else:
                # Para los demás elementos, muestra el texto normalmente
                user_info_layout.add_widget(Button(text=f"{key}: {value}", size_hint_y=None, height=50))


        # Botón para volver a la pantalla principal
        back_button = Button(text="Regresar", size_hint_y=None, height=50)
        back_button.bind(on_release=self.go_back)

        user_info_layout.add_widget(back_button)

        # Agrega el layout al ScrollView
        scroll_view.add_widget(user_info_layout)

        # Agrega el ScrollView al contenido
        content.add_widget(scroll_view)

        # Cambia a la pantalla de visualización de usuario
        self.ids.scrn_mngr.current = 'scrn_view'

    def ver_documento(self, url):
        # Lógica para abrir el documento específico
        if url:  # Asegúrate de que el URL no esté vacío
            webbrowser.open(url)
        else:
            print("URL no disponible para este documento")

    def go_back(self, instance):
        self.ids.scrn_mngr.current = 'scrn_content'



    def get_users(self, mode, id, conv):
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

            sql = 'SELECT * FROM Aspirante WHERE estado_solicitud = %s AND convocatoria = %s'
            mycursor.execute(sql, ("Pendiente", conv))

            users = mycursor.fetchall()
            for user in users:
                ids.append(user[0])
                first_names.append(user[6])
                last_names.append(user[7])
                user_names.append(user[8])
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
                'ID', 'nombres', 'apellidoPat', 'apellidoMat', 'Fecha Nacimiento', 'edad',
                'genero', 'telefono', 'nacionalidad', 'CURP', 'correo', 
                'nivelEducativo', 'Lengua Indigena', 'Nivel Preferido', 'Experiencia Cientifica',
                'Habilidades', 'Razon', 'Profesion', 'Requisito para titulo', 'Codigo Postal', 'Estado', 'Municipio',
                'Estado Preferente', 'Ciclo', 'Municipio Deseado', 'Doc1', 'Doc2', 'Doc3'
            ]

            # Crear OrderedDict usando una comprensión

            _users = OrderedDict((key, {}) for key in keys)


            sql = 'SELECT * FROM Aspirante WHERE id_Aspirante = %s'
            mycursor.execute(sql, (id,))

            users = mycursor.fetchall()
            idx = 0

            for user in users:
                _users['ID'][idx] = user[0]
                _users['nombres'][idx] = user[7]
                _users['apellidoPat'][idx] = user[8]
                _users['apellidoMat'][idx] = user[9]
                _users['Fecha Nacimiento'][idx] = user[10]
                _users['edad'][idx] = user[6]
                _users['genero'][idx] = user[11]
                _users['telefono'][idx] = user[3]
                _users['nacionalidad'][idx] = user[12]
                _users['CURP'][idx] = user[5]
                _users['correo'][idx] = user[4]
            
            sql = 'SELECT * FROM InfoEducativaAspirante WHERE id_Aspirante = %s'
            mycursor.execute(sql, (id,))

            users = mycursor.fetchall()

            for user in users:
                _users['nivelEducativo'][idx] = user[2]
                _users['Lengua Indigena'][idx] = user[4]
                _users['Nivel Preferido'][idx] = user[5]
                _users['Experiencia Cientifica'][idx] = user[6]
                _users['Habilidades'][idx] = user[7]
                _users['Razon'][idx] = user[9]
                _users['Profesion'][idx] = user[10]
                _users['Requisito para titulo'][idx] = user[11]

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

            sql = 'SELECT * FROM DocumentosAspirante WHERE id_Aspirante = %s'
            mycursor.execute(sql, (id,))

            users = mycursor.fetchall()

            for user in users:
                _users['Doc1'][idx] = user[1]
                _users['Doc2'][idx] = user[2]
                _users['Doc3'][idx] = user[3]

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