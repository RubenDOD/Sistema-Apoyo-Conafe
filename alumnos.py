from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from collections import OrderedDict
from utils.datatable_alumnos import DataTableAlumnos
from datetime import datetime
import hashlib
import mysql.connector
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

class AlumnosWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Builder.load_file("alumnos.kv")
        # Conexión a la base de datos
        self.mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='CONAFE'
        )
        self.mycursor = self.mydb.cursor()

        # Cargar contenido inicial
        content = self.ids.scrn_contents
        users = self.get_users("General", 0)
        userstable = DataTableAlumnos(table=users, callback=self.button_callback)  # Pasa button_callback aquí
        content.add_widget(userstable)

    def reload_users(self):
        """Recarga la lista de usuarios en la pantalla principal."""
        content = self.ids.scrn_contents
        content.clear_widgets()
        users = self.get_users("General", 0)
        userstable = DataTableAlumnos(table=users, callback=self.button_callback)
        content.add_widget(userstable)

    def button_callback(self, button_text, idx):
        """Callback para manejar acciones en la tabla."""
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

    def only_letters(self, substring, from_undo):
        """Permite solo letras del alfabeto español."""
        valid_chars = "abcdefghijklmnopqrstuvwxyzáéíóúüñABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚÜÑ "
        return ''.join([char for char in substring if char in valid_chars])

    def only_numbers(self, substring, from_undo):
        """Permite solo números."""
        return ''.join([char for char in substring if char.isdigit()])

    def alphanumeric(self, substring, from_undo):
        """Permite solo caracteres alfanuméricos."""
        return ''.join([char for char in substring if char.isalnum()])
    
    def ver_user(self, idx, conv_id):
        """Muestra detalles de un usuario."""
        if 'AdminWindow' in self.ids.scrn_mngr.screen_names:
            screen_to_remove = self.ids.scrn_mngr.get_screen('AdminWindow')
            self.ids.scrn_mngr.remove_widget(screen_to_remove)

        conv_admin_screen = AdminWindow(name='AdminWindow', conv=conv_id)
        self.ids.scrn_mngr.add_widget(conv_admin_screen)
        self.ids.scrn_mngr.current = 'AdminWindow'

    def go_back_to_convocatorias(self):
        """Regresa a la pantalla principal."""
        self.ids.scrn_mngr.current = 'scrn_content'
        self.reload_users()

    def add_user_fields(self):
        """Cambia a la pantalla del formulario de usuario."""
        self.ids.scrn_mngr.current = 'add_user_form'

    def save_user(self):
        """Guarda los datos de un nuevo usuario en la base de datos con validaciones."""
        curp = self.ids.curp.text.strip().upper()  # Convertir a mayúsculas
        nombres = self.ids.nombres.text.strip()
        apellido_paterno = self.ids.apellido_paterno.text.strip()
        apellido_materno = self.ids.apellido_materno.text.strip()
        dia = self.ids.dia.text.strip()
        mes = self.ids.mes.text.strip()
        anio = self.ids.anio.text.strip()
        nivel = self.ids.nivel.text.strip()
        grado = self.ids.grado.text.strip()

        # Validaciones
        if not all([curp, nombres, apellido_paterno, dia, mes, anio, nivel, grado]):
            self.show_popup("Revisar datos", "Todos los campos son obligatorios.")
            return

        if len(curp) < 10 or len(curp) > 16:
            self.show_popup("Revisar datos", "El CURP debe tener al menos 10 caracteres y maximo 16.")
            return

        if len(nombres) < 2 or len(nombres) > 50:
            self.show_popup("Revisar datos", "El nombre debe tener al menos 2 caracteres y menos de 50.")
            return

        if len(apellido_paterno) < 2 or len(apellido_paterno) > 25:
            self.show_popup("Revisar datos", "El apellido paterno debe tener al menos 2 caracteres y menos de 25.")
            return

        if len(apellido_materno) < 2 or len(apellido_paterno) > 25:
            self.show_popup("Revisar datos", "El apellido materno debe tener al menos 2 caracteres y menos de 25.")
            return

        # Verificar si el CURP ya existe
        try:
            self.mycursor.execute("SELECT COUNT(*) FROM alumno WHERE CURP = %s", (curp,))
            if self.mycursor.fetchone()[0] > 0:
                self.show_popup("Error", "El CURP ya está registrado.")
                return
        except Exception as e:
            self.show_popup("Error", f"Error al verificar el CURP: {e}")
            return

        # Validar la fecha de nacimiento
        try:
            fecha_nacimiento = datetime.strptime(f"{anio}-{mes}-{dia}", "%Y-%m-%d")
            if fecha_nacimiento.year < 1980:
                self.show_popup("Revisar datos", "El año de nacimiento debe ser mayor a 1980.")
                return
        except ValueError:
            self.show_popup("Revisar datos", "La fecha ingresada no es válida.")
            return

        # Inserción en la base de datos
        try:
            sql = """
                INSERT INTO alumno (CURP, nombres, apellido_paterno, apellido_materno, fechaNacimiento, nivel, grado)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (curp, nombres, apellido_paterno, apellido_materno, fecha_nacimiento.strftime("%Y-%m-%d"), nivel, grado)
            self.mycursor.execute(sql, values)
            self.mydb.commit()
            self.show_popup("Éxito", "Usuario agregado exitosamente.")  # Mostrar Popup de éxito
        except Exception as e:
            self.show_popup("Error", f"Error al guardar el usuario: {e}")

        # Limpiar formulario
        self.ids.curp.text = ''
        self.ids.nombres.text = ''
        self.ids.apellido_paterno.text = ''
        self.ids.apellido_materno.text = ''
        self.ids.dia.text = ''
        self.ids.mes.text = ''
        self.ids.anio.text = ''
        self.ids.nivel.text = 'Seleccionar Nivel'
        self.ids.grado.text = 'Seleccionar Grado'

    def show_popup(self, title, message):
        """Muestra un Popup con un mensaje."""
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.8, 0.4),
            auto_dismiss=True
        )
        popup.open()


    def go_back_to_users(self):
        """Regresa a la pantalla principal desde el formulario."""
        self.ids.scrn_mngr.current = 'scrn_content'

    def get_users(self, mode, id):
        """Obtiene la lista de usuarios desde la base de datos."""
        if mode == "General":
            _alumnos = OrderedDict()
            _alumnos['CURP'] = {}
            _alumnos['nombres'] = {}
            _alumnos['apellido_paterno'] = {}
            _alumnos['nivel'] = {}
            ids = []
            nombres = []
            apellidos = []
            niveles = []

            sql = 'SELECT * FROM alumno'
            self.mycursor.execute(sql)

            users = self.mycursor.fetchall()
            for user in users:
                ids.append(user[0])
                nombres.append(user[1])
                apellidos.append(user[2])
                niveles.append(user[5])

            users_length = len(nombres)
            idx = 0
            while idx < users_length:
                _alumnos['CURP'][idx] = ids[idx]
                _alumnos['nombres'][idx] = nombres[idx]
                _alumnos['apellido_paterno'][idx] = apellidos[idx]
                _alumnos['nivel'][idx] = niveles[idx]
                idx += 1

            return _alumnos


class AlumnosApp(App):
    def build(self):
        return AlumnosWindow()


if __name__ == '__main__':
    AlumnosApp().run()