from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from collections import OrderedDict
from utils.datatable_alumnosMod import DataTableAlumnosMod
from datetime import datetime
import hashlib
import mysql.connector
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

class ModificarAlumnoWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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
        userstable = DataTableAlumnosMod(table=users, callback=self.button_callback)  # Pasa button_callback aquí
        content.add_widget(userstable)

    def reload_users(self):
        """Recarga la lista de usuarios en la pantalla principal."""
        content = self.ids.scrn_contents
        content.clear_widgets()
        users = self.get_users("General", 0)
        userstable = DataTableAlumnosMod(table=users, callback=self.button_callback)
        content.add_widget(userstable)

    def button_callback(self, button_text, idx):
        
        if button_text == 'Modificar':

            user_data = self.get_users("Specific", idx)
            print(user_data)
            self.ids.curp.text = user_data['CURP'][0]  # Llenar CURP
            self.ids.nombres.text = user_data['nombres'][0]  # Llenar nombres
            self.ids.apellido_paterno.text = user_data['apellido_paterno'][0]  # Llenar apellido paterno
            self.ids.apellido_materno.text = user_data['apellido_materno'][0]  # Llenar apellido materno
            self.ids.dia.text = str(user_data['fechaNacimiento'][0].day)  # Llenar día
            self.ids.mes.text = str(user_data['fechaNacimiento'][0].month)  # Llenar mes
            self.ids.anio.text = str(user_data['fechaNacimiento'][0].year)  # Llenar año
            self.ids.nivel.text = user_data['nivel'][0]  # Llenar nivel
            self.ids.grado.text = user_data['grado'][0]  # Llenar grado
            # Hacer el campo de CURP no editable
            self.ids.curp.readonly = True

            # Opcional: Mostrar el mensaje de modificación
            self.ids.nombres.focus = True  # Establecer el foco en el primer campo editable

        # Cambiar a la pantalla de formulario
            self.ids.scrn_mngr.current = 'add_user_form'  # Cambiar pantalla al formulario
        elif button_text == 'Borrar':
        # Mostrar el Popup de confirmación para borrar el alumno
            self.show_delete_popup(idx)

    def show_delete_popup(self, idx):
        """Muestra un Popup para confirmar la eliminación del alumno."""
        popup_content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Mensaje de confirmación
        message = Label(text="¿Estás seguro de que deseas eliminar este alumno?", size_hint_y=None, height=40)
        
        # Botones de confirmación
        btn_confirmar = Button(text="Confirmar", size_hint_y=None, height=40)
        btn_cancelar = Button(text="Cancelar", size_hint_y=None, height=40)
        
        popup_content.add_widget(message)
        popup_content.add_widget(btn_confirmar)
        popup_content.add_widget(btn_cancelar)
        
        # Crear el Popup
        popup = Popup(title="Confirmar eliminación",
                    content=popup_content,
                    size_hint=(0.6, 0.4),
                    auto_dismiss=False)

        # Acción cuando se confirma la eliminación
        def confirm_delete(instance):
            user_data = self.get_users("Specific", idx)
            curp = user_data['CURP'][0]  # Obtener el CURP del alumno
            self.delete_user(curp)  # Eliminar al alumno
            popup.dismiss()  # Cerrar el popup

        # Acción cuando se cancela la eliminación
        def cancel_delete(instance):
            popup.dismiss()  # Solo cerrar el popup sin hacer nada

        # Asignar las acciones a los botones
        btn_confirmar.bind(on_press=confirm_delete)
        btn_cancelar.bind(on_press=cancel_delete)
        
        popup.open()  # Abrir el Popup

    def delete_user(self, curp):
        """Elimina un alumno de la base de datos."""
        try:
            # Eliminar el alumno con el CURP especificado
            sql = "DELETE FROM alumno WHERE CURP = %s"
            self.mycursor.execute(sql, (curp,))
            self.mydb.commit()
            
            # Mostrar un mensaje de éxito
            self.show_popup("Éxito", f"Alumno con CURP {curp} eliminado exitosamente.")
            self.reload_users()  # Recargar la lista de usuarios después de eliminar

        except Exception as e:
            # Mostrar un mensaje de error si ocurre algún problema
            self.show_popup("Error", f"Error al eliminar el alumno: {e}")

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

    def go_back_to_convocatorias(self):
        """Regresa a la pantalla principal."""
        try:
            app = App.get_running_app()  # Obtén la instancia de la aplicación principal
            app.root.current = "vista_gestion_alumnos"  # Cambia a la pantalla específica
            print("Regresando a la pantalla 'vista_gestion_alumnos'")
        except Exception as e:
            print(f"Error al regresar a la pantalla: {e}")
    
    def go_back_to_table(self):
        """Regresa a la pantalla principal."""
        try:
            self.ids.scrn_mngr.current = 'scrn_content'
        except Exception as e:
            print(f"Error al regresar a la pantalla: {e}")

    def add_user_fields(self):
        """Cambia a la pantalla del formulario de usuario."""
        self.ids.scrn_mngr.current = 'add_user_form'

    def save_user(self):
        """Actualiza los datos de un usuario existente en la base de datos con validaciones."""
        curp = self.ids.curp.text.strip().upper()  # Convertir a mayúsculas
        nombres = self.ids.nombres.text.strip()
        apellido_paterno = self.ids.apellido_paterno.text.strip()
        apellido_materno = self.ids.apellido_materno.text.strip()
        dia = self.ids.dia.text.strip()
        mes = self.ids.mes.text.strip()
        anio = self.ids.anio.text.strip()
        nivel = self.ids.nivel.text.strip()
        grado = self.ids.grado.text.strip()
        print(curp)
        # Validaciones
        if not all([curp, nombres, apellido_paterno, dia, mes, anio, nivel, grado]):
            self.show_popup("Revisar datos", "Todos los campos son obligatorios.")
            return

        if len(curp) < 10 or len(curp) > 18:
            self.show_popup("Revisar datos", "El CURP debe tener al menos 10 caracteres y máximo 18.")
            return

        if len(nombres) < 2 or len(nombres) > 50:
            self.show_popup("Revisar datos", "El nombre debe tener al menos 2 caracteres y menos de 50.")
            return

        if len(apellido_paterno) < 2 or len(apellido_paterno) > 25:
            self.show_popup("Revisar datos", "El apellido paterno debe tener al menos 2 caracteres y menos de 25.")
            return

        if len(apellido_materno) < 2 or len(apellido_materno) > 25:
            self.show_popup("Revisar datos", "El apellido materno debe tener al menos 2 caracteres y menos de 25.")
            return

        # Verificar si el CURP existe en la base de datos
        try:
            self.mycursor.execute("SELECT COUNT(*) FROM alumno WHERE CURP = %s", (curp,))
            if self.mycursor.fetchone()[0] == 0:
                self.show_popup("Error", "El CURP no está registrado.")
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

        # Actualización de los datos en la base de datos
        try:
            sql = """
                UPDATE alumno
                SET nombres = %s, apellido_paterno = %s, apellido_materno = %s, 
                    fechaNacimiento = %s, nivel = %s, grado = %s
                WHERE CURP = %s
            """
            values = (nombres, apellido_paterno, apellido_materno, 
                    fecha_nacimiento.strftime("%Y-%m-%d"), nivel, grado, curp)
            self.mycursor.execute(sql, values)
            self.mydb.commit()
            self.show_popup("Éxito", "Datos de usuario actualizados exitosamente.")  # Mostrar Popup de éxito
        except Exception as e:
            self.show_popup("Error", f"Error al actualizar los datos del usuario: {e}")

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
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                passwd='1234',
                database='CONAFE'
            )
            mycursor = mydb.cursor()
            
            try:
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

                    # Consulta para obtener alumnos que no están en la tabla alumnoCCT
                    sql = '''
                        SELECT a.CURP, a.nombres, a.apellido_paterno, a.nivel
                        FROM alumno a
                        LEFT JOIN alumnoCCT ac ON a.CURP = ac.id_alumno
                        WHERE ac.id_alumno IS NULL
                    '''
                    mycursor.execute(sql)

                    users = mycursor.fetchall()
                    for user in users:
                        ids.append(user[0])  # CURP
                        nombres.append(user[1])  # Nombres
                        apellidos.append(user[2])  # Apellido paterno
                        niveles.append(user[3])  # Nivel

                    users_length = len(nombres)
                    idx = 0
                    while idx < users_length:
                        _alumnos['CURP'][idx] = ids[idx]
                        _alumnos['nombres'][idx] = nombres[idx]
                        _alumnos['apellido_paterno'][idx] = apellidos[idx]
                        _alumnos['nivel'][idx] = niveles[idx]
                        idx += 1

                    return _alumnos

                else:  # Filtrar por CURP
                    _alumnos = OrderedDict()
                    _alumnos['CURP'] = {}
                    _alumnos['nombres'] = {}
                    _alumnos['apellido_paterno'] = {}
                    _alumnos['apellido_materno'] = {}
                    _alumnos['fechaNacimiento'] = {}
                    _alumnos['nivel'] = {}
                    _alumnos['grado'] = {}

                    sql = 'SELECT * FROM alumno WHERE CURP = %s'
                    mycursor.execute(sql, (id,))
                    users = mycursor.fetchall()

                    for idx, user in enumerate(users):
                        _alumnos['CURP'][idx] = user[0]
                        _alumnos['nombres'][idx] = user[1]
                        _alumnos['apellido_paterno'][idx] = user[2]
                        _alumnos['apellido_materno'][idx] = user[3]
                        _alumnos['fechaNacimiento'][idx] = user[4]
                        _alumnos['nivel'][idx] = user[5]
                        _alumnos['grado'][idx] = user[6]

                    return _alumnos
            finally:
                # Cierra el cursor y la conexión
                mycursor.close()
                mydb.close()


class ModificarAlumnoApp(App):
    def build(self):
        return ModificarAlumnoWindow()


if __name__ == '__main__':
    ModificarAlumnoApp().run()