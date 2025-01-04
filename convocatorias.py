from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from collections import OrderedDict
from utils.datatable_convocatorias import DataTableConv
from datetime import datetime
import hashlib
from db_connection import execute_query
from db_connection import execute_non_query
from añadir_convocatoria import AddConvoScreen
from kivy.uix.boxlayout import BoxLayout
import webbrowser
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from admin import AdminWindow
from EditConvocatoria import EditConvocatoriaWindow

class ConvocatoriaWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Builder.load_file("convocatorias.kv")  # Carga explícita de admin.kv
        Builder.load_file("admin.kv")
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
        elif button_text == 'Cambios':
            self.users = self.get_users("General", 0)
            conv_id = self.users['ID'][idx]
            self.editar_convocatoria(conv_id)
        
        self.reload_users()

    def editar_convocatoria(self, conv_id):
        # Verifica si la pantalla ya está en el ScreenManager
        if 'edit_convo_app' not in self.ids.scrn_mngr.screen_names:
            # Si no está registrada, añade la pantalla
            edit_screen = EditConvocatoriaWindow(conv_id=conv_id, name='edit_convo_app')
            self.ids.scrn_mngr.add_widget(edit_screen)
        
        # Cambia a la pantalla de edición
        self.ids.scrn_mngr.current = 'edit_convo_app'

    def abrir_convocatoria(self, conv_id):
        """Abre una convocatoria cambiando su estado en la base de datos."""
        try:
            sql = "UPDATE ConvocatoriaActual SET estado_convocatoria = ? WHERE id_Convo = ?"
            execute_non_query(sql, ("Abierta", conv_id))
            print(f"Convocatoria {conv_id} abierta con éxito.")
        except Exception as e:
            print(f"Error al abrir convocatoria {conv_id}: {e}")

    def cerrar_convocatoria(self, conv_id):
        """Cierra una convocatoria cambiando su estado en la base de datos."""
        try:
            sql = "UPDATE ConvocatoriaActual SET estado_convocatoria = ? WHERE id_Convo = ?"
            execute_non_query(sql, ("Cerrada", conv_id))
            self.reload_users()
            print(f"Convocatoria {conv_id} cerrada con éxito.")
        except Exception as e:
            print(f"Error al cerrar convocatoria {conv_id}: {e}")

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
        """Obtiene la lista de usuarios o convocatorias desde la base de datos."""
        try:
            if mode == "General":
                _convocatorias = OrderedDict()
                _convocatorias['ID'] = {}
                _convocatorias['nombre'] = {}
                _convocatorias['status'] = {}

                ids = []
                nombres = []
                status = []

                sql = 'SELECT * FROM ConvocatoriaActual'
                users = execute_query(sql)

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

        except Exception as e:
            print(f"Error al obtener usuarios: {e}")
            return None
        
    def change_screen(self, instance):
        if instance.text == 'Manage Users':
            self.ids.scrn_mngr.current = 'scrn_content'

class ConvocatoriasApp(App):
    def build(self):

        return ConvocatoriaWindow()

if __name__=='__main__':
    ConvocatoriasApp().run()