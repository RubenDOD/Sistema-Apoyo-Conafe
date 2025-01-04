from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.lang import Builder
from db_connection import execute_query
import re  # Para validación del correo

class UpdateCorreoWindow(BoxLayout):
    def __init__(self, id_aspirante=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.aspirante_id = id_aspirante  # Asignar el id_aspirante recibido

        # Cargar los datos del aspirante
        self.cargar_datos()

    def cargar_datos(self):
        """Carga los datos del aspirante desde la base de datos."""
        # Consultar los datos actuales del aspirante
        select_query = """
        SELECT telefonoFijo, telefonoMovil, correo
        FROM Aspirante
        WHERE id_Aspirante = %s
        """
        try:
            result = execute_query(select_query, (self.aspirante_id,))
            if result:
                self.ids.telefono_fijo.text = result[0]['telefonoFijo']
                self.ids.telefono_movil.text = result[0]['telefonoMovil']
                self.ids.correo.text = result[0]['correo']
        except Exception as e:
            self.mostrar_error(f"Error al cargar los datos: {e}")

    def guardar_cambios(self):
        """Guarda los cambios realizados en los datos del aspirante."""
        telefono_fijo = self.ids.telefono_fijo.text
        telefono_movil = self.ids.telefono_movil.text
        correo = self.ids.correo.text

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
            print("Datos actualizados exitosamente.")
        except Exception as e:
            self.mostrar_error(f"Error al actualizar los datos: {e}")

    def mostrar_error(self, mensaje):
        """Muestra un popup con un mensaje de error."""
        popup = Popup(
            title='Error',
            content=Label(text=mensaje),
            size_hint=(None, None),
            size=(400, 200)
        )
        popup.open()

    def validar_correo(self, correo):
        """Valida el formato del correo usando una expresión regular."""
        regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(regex, correo) is not None

    def validar_telefono(self, instancia, valor):
        """Permite solo números y el símbolo '+' en los campos de teléfono."""
        if not all(c.isdigit() or c == '+' for c in valor):
            instancia.text = valor[:-1]  # Elimina el último carácter si no es válido

class UpdateCorreo(App):
    def build(self):
        # Aquí le pasas el ID del aspirante al formulario
        return UpdateCorreoWindow(id_aspirante=1)  # Cambia el ID según sea necesario

if __name__ == '__main__':
    UpdateCorreo().run()
