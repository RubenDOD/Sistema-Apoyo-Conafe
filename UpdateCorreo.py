import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from db_connection import execute_query
import re  # Para validación del correo

class UpdateCorreoWindow(BoxLayout):
    def __init__(self, id_aspirante = None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.aspirante_id = id_aspirante  # Asignar el id_aspirante recibido

        # Cargar los datos del aspirante
        self.cargar_datos()

    def solicitar_apoyo(self, apoyo):
        """Solicita un apoyo para el educador si aún no lo tiene."""
        # Verificar si el usuario ya tiene un apoyo
        query = "SELECT * FROM apoyo_educador WHERE id_educador = %s"
        resultado = execute_query(query, (self.id_educador,))

        print("Apoyos con los que ya cuenta el usuario:", resultado)

        # Verificar si el usuario ya tiene el apoyo solicitado
        for result in resultado:
            if result['id_apoyo'] == apoyo['id_apoyo']:
                # Mostrar mensaje de error si el apoyo ya existe
                popup = Popup(
                    title='Error',
                    content=Label(text='Ya cuentas con este apoyo.'),
                    size_hint=(0.6, 0.4)
                )
                popup.open()
                return

        # Insertar el nuevo apoyo para el usuario
        insert_query = """
            INSERT INTO apoyo_educador (id_apoyo, id_educador, estado_apoyo)
            VALUES (%s, %s, 'pendiente')
        """
        execute_query(insert_query, (apoyo['id_apoyo'], self.id_educador))

        # Mostrar mensaje de éxito
        popup = Popup(
            title='Éxito',
            content=Label(text='Has solicitado el apoyo exitosamente.'),
            size_hint=(0.6, 0.4)
        )
        popup.open()

    def guardar_cambios(self):
        telefono_fijo = self.ids.telefono_fijo.text.strip()
        telefono_movil = self.ids.telefono_movil.text.strip()
        correo = self.ids.correo.text.strip()

        # Validaciones
        if not self.validar_correo(correo):
            self.mostrar_error("El correo no es válido.")
            return

        if len(correo) > 50:
            self.mostrar_error("El correo no puede exceder los 50 caracteres.")
            return

        if len(telefono_fijo) > 15 or len(telefono_movil) > 15:
            self.mostrar_error("El teléfono no puede exceder los 15 caracteres.")
            return

        if len(telefono_fijo) < 6 or len(telefono_movil) < 6 or len(correo) < 6:
            self.mostrar_error("Los datos deben tener al menos 6 caracteres.")
            return

        if not telefono_fijo or not telefono_movil or not correo:
            self.mostrar_error("No se pueden dejar campos vacíos.")
            return

        # Actualizar los datos del aspirante en la base de datos
        update_query = """
        UPDATE Aspirante
        SET telefonoFijo = %s, telefonoMovil = %s, correo = %s
        WHERE id_Aspirante = %s
        """
        try:
            execute_query(update_query, (telefono_fijo, telefono_movil, correo, self.aspirante_id))
            self.mostrar_mensaje("Éxito", "Datos actualizados exitosamente.")
        except Exception as e:
            self.mostrar_error(f"Error al actualizar los datos: {e}")

    def mostrar_error(self, mensaje):
        # Crear un popup para mostrar el mensaje de error
        popup = Popup(title='Error',
                      content=Label(text=mensaje),
                      size_hint=(None, None), size=(400, 200))
        popup.open()

    def validar_correo(self, correo):
        # Expresión regular básica para validar el formato del correo
        regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(regex, correo) is not None

    def validar_telefono(self, instancia, valor):
        # Permitir solo números y el símbolo '+'
        if not all(c.isdigit() or c == '+' for c in valor):
            instancia.text = valor[:-1]  # Elimina el último carácter si no es válido

class UpdateCorreo(App):
    def build(self):
        # Aquí le pasas el ID del aspirante al formulario
        return UpdateCorreoWindow()  # Cambia el ID según sea necesario

if __name__ == '__main__':
    UpdateCorreo().run()
