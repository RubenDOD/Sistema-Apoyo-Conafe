from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from collections import OrderedDict
from utils.datatable_convocatorias import DataTableConv
from datetime import datetime
import hashlib
import mysql.connector
from añadir_convocatoria import AddConvoScreen
from kivy.uix.boxlayout import BoxLayout
import webbrowser
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from admin import AdminWindow

class ConvocatoriaWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Builder.load_file("convocatorias.kv")  # Carga explícita de admin.kv
        Builder.load_file("admin.kv")
        self.mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='CONAFE'
        )
        self.mycursor = self.mydb.cursor()

        content = self.ids.scrn_contents
        users = self.get_users("General", 0)
        userstable = DataTableConv(table=users, callback=self.button_callback)  # Pasa button_callback aquí
        content.add_widget(userstable)

         # Crear una pantalla compatible y agregar `addConvoApp` como widget
        convo_screen = Screen(name='add_convo_app')
        convo_layout = BoxLayout()  # Asegura que el layout sea compatible con `addConvoApp`
        convo_layout.add_widget(AddConvoScreen(convocatoria_window=self))
        convo_screen.add_widget(convo_layout)
        
        self.ids.scrn_mngr.add_widget(convo_screen)

        if not users or all(len(col) == 0 for col in users.values()):
            # Cambia directamente a la pantalla add_convo_app si no hay usuarios
            self.ids.scrn_mngr.current = 'add_convo_app'

    def reload_users(self):
        # Obtiene el contenedor de usuarios
        content = self.ids.scrn_contents
        content.clear_widgets()

        # Obtiene nuevamente la lista de usuarios
        users = self.get_users("General", 0)

        # Crea la tabla actualizada y agrégala a la pantalla
        userstable = DataTableConv(table=users, callback=self.button_callback)
        content.add_widget(userstable)

    def button_callback(self, button_text, idx):
        if button_text == 'Abrir':
            self.users = self.get_users("General", 0)
            conv_id = self.users['ID'][idx]
            self.abrir_convocatoria(conv_id)
        elif button_text == 'Cerrar':
            self.users = self.get_users("General", 0)
            conv_id = self.users['ID'][idx]
            self.cerrar_convocatoria(conv_id)
        elif button_text == 'Ver':
            self.users = self.get_users("General", 0)
            conv_id = self.users['ID'][idx]
            self.ver_user(idx, conv_id)
        self.reload_users()

    def abrir_convocatoria(self, conv_id):
        # Conexión a la base de datos
        db = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='CONAFE'
        )
        cursor = db.cursor()

        sql = "UPDATE ConvocatoriaActual SET estado_convocatoria = %s WHERE id_Convo = %s"
        cursor.execute(sql, ("Abierta", conv_id))
        db.commit()  # Guarda los cambios

        # Cierra el cursor y la conexión
        cursor.close()
        db.close()
        print(f"Convocatoria {conv_id} abierta con éxito.")

    def cerrar_convocatoria(self, conv_id):
        # Conexión a la base de datos
        db = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='CONAFE'
        )
        cursor = db.cursor()
        self.reload_users()

        sql = "UPDATE ConvocatoriaActual SET estado_convocatoria = %s WHERE id_Convo = %s"
        cursor.execute(sql, ("Cerrada", conv_id))
        db.commit()  # Guarda los cambios

        # Cierra el cursor y la conexión
        cursor.close()
        db.close()
        print(f"Convocatoria {conv_id} Cerrada con éxito.")

    def ver_user(self, idx, conv_id):
        # Eliminar pantalla 'AdminWindow' si ya existe, para evitar duplicados
        if 'AdminWindow' in self.ids.scrn_mngr.screen_names:
            screen_to_remove = self.ids.scrn_mngr.get_screen('AdminWindow')
            self.ids.scrn_mngr.remove_widget(screen_to_remove)

        # Crear una nueva instancia de AdminWindow con el conv_id seleccionado
        conv_admin_screen = AdminWindow(name='AdminWindow', conv=conv_id)
        self.ids.scrn_mngr.add_widget(conv_admin_screen)
        self.ids.scrn_mngr.current = 'AdminWindow'

    def go_back(self, instance):
        # Verifica si la pantalla actual es la pantalla inicial
        if self.ids.scrn_mngr.current == 'scrn_content':  # 'scrn_content' como la pantalla principal
            # Si estamos en la pantalla inicial, regresa a VistaDireccionTerritorialScreen
            App.get_running_app().root.current = 'vista_direccion_territorial'
        else:
            # Si no estamos en la pantalla inicial, vuelve a la pantalla anterior dentro de ConvocatoriaWindow
            self.ids.scrn_mngr.current = 'scrn_content'

    def add_user_fields(self):
        self.ids.scrn_mngr.current = 'add_convo_app'
        self.reload_users   

    def get_users(self, mode, id):
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='CONAFE'
        )
        mycursor = mydb.cursor()

        if mode == "General":
            _convocatorias = OrderedDict()
            _convocatorias['ID'] = {}
            _convocatorias['nombre'] = {}
            _convocatorias['status'] = {}
            ids = []
            nombres = []
            status = []


            sql = 'SELECT * FROM ConvocatoriaActual'
            mycursor.execute(sql)

            users = mycursor.fetchall()
            for user in users:
                ids.append(user[0])
                nombres.append(user[1])
                status.append(user[4])

            users_length = len(nombres)
            idx = 0
            while idx < users_length:
                _convocatorias['ID'][idx] = ids[idx]
                _convocatorias['nombre'][idx] = nombres[idx]
                _convocatorias['status'][idx] = status[idx]
                idx += 1
            
            return _convocatorias

    
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
        if instance.text == 'Manage Users':
            self.ids.scrn_mngr.current = 'scrn_content'

class ConvocatoriasApp(App):
    def build(self):

        return ConvocatoriaWindow()

if __name__=='__main__':
    ConvocatoriasApp().run()