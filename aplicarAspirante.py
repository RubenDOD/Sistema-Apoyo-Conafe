from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from collections import OrderedDict
from utils.datatable_convocatoriasUser import DataTableConvUser
from datetime import datetime
import hashlib
import mysql.connector
from kivy.uix.boxlayout import BoxLayout
import webbrowser
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

class aplicarAspiranteWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Builder.load_file("aplicarAspirante.kv")  # Carga explícita de admin.kv
        self.mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='CONAFE'
        )
        self.mycursor = self.mydb.cursor()

        content = self.ids.scrn_contents
        users = self.get_users("General", 0)
        userstable = DataTableConvUser(table=users, callback=self.button_callback)  # Pasa button_callback aquí
        content.add_widget(userstable)

    def go_back(self, instance):
        app = App.get_running_app()
        app.root.current = 'aspirante'  # Cambia a la pantalla 'aspirante'

    def reload_users(self):
        # Obtiene el contenedor de usuarios
        content = self.ids.scrn_contents
        content.clear_widgets()

        # Obtiene nuevamente la lista de usuarios
        users = self.get_users("General", 0)

        # Crea la tabla actualizada y agrégala a la pantalla
        userstable = DataTableConvUser(table=users, callback=self.button_callback)
        content.add_widget(userstable)

    def button_callback(self, button_text, idx):
        if button_text == 'Ver':
            self.users = self.get_users("General", 0)
            conv_id = self.users['ID'][idx]
            self.abrir_documento(conv_id)
        elif button_text == 'Aplicar':
            self.users = self.get_users("General", 0)
            conv_id = self.users['ID'][idx]
            self.abrir_forms(conv_id)

    def abrir_documento(self, conv_id):
        # Conexión a la base de datos
        db = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='CONAFE'
        )
        cursor = db.cursor()

        sql = "SELECT url_convocatoria FROM ConvocatoriaActual WHERE id_Convo = %s"
        cursor.execute(sql, (conv_id,))

        # Obtiene la URL y la abre
        url = cursor.fetchone()
        if url:
            webbrowser.open(url[0])  # Abre la URL en el navegador
            print(f"Convocatoria {conv_id} abierta con éxito.")
        else:
            print(f"No se encontró la convocatoria con ID {conv_id}.")

        # Cierra el cursor y la conexión
        cursor.close()
        db.close()

        

    def abrir_forms(self, conv_id):
        # Conexión a la base de datos
        db = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='CONAFE'
        )
        cursor = db.cursor()

        sql = "SELECT url_forms FROM ConvocatoriaActual WHERE id_Convo = %s"
        cursor.execute(sql, (conv_id,))

        # Obtiene la URL y la abre
        url = cursor.fetchone()
        if url:
            webbrowser.open(url[0])  # Abre la URL en el navegador
            print(f"Convocatoria {conv_id} abierta con éxito.")
        else:
            print(f"No se encontró la convocatoria con ID {conv_id}.")

        # Cierra el cursor y la conexión
        cursor.close()
        db.close()


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


            sql = 'SELECT * FROM ConvocatoriaActual WHERE estado_convocatoria = "Abierta"'
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


    def change_screen(self, instance):
        if instance.text == 'Manage Users':
            self.ids.scrn_mngr.current = 'scrn_content'



class aplicarAspiranteApp(App):
    def build(self):

        return aplicarAspiranteWindow()

if __name__=='__main__':
    aplicarAspiranteApp().run()