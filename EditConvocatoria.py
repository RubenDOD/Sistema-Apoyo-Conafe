from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from db_connection import execute_query

class EditConvocatoriaWindow(Screen):
    def __init__(self, conv_id=None, **kwargs):
        super().__init__(**kwargs)
        self.conv_id = conv_id

        # Layout de la pantalla
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Campos para el nombre y URLs
        self.layout.add_widget(Label(text="Nombre de Convocatoria:"))
        self.nombre_input = TextInput()
        self.layout.add_widget(self.nombre_input)

        self.layout.add_widget(Label(text="URL de Convocatoria:"))
        self.url_input = TextInput()
        self.layout.add_widget(self.url_input)

        self.layout.add_widget(Label(text="URL de Formulario:"))
        self.url_form_input = TextInput()
        self.layout.add_widget(self.url_form_input)

        # Botón para actualizar
        self.update_button = Button(text="Actualizar Convocatoria")
        self.update_button.bind(on_press=self.actualizar_convocatoria)
        self.layout.add_widget(self.update_button)

        # Cargar los datos actuales de la convocatoria
        self.cargar_datos()

        self.add_widget(self.layout)

    def cargar_datos(self):
        try:
            # Obtener los datos de la convocatoria por ID
            sql = """
                SELECT nombre_convocatoria, url_convocatoria, url_forms
                FROM ConvocatoriaActual
                WHERE id_Convo = ?
            """
            data = execute_query(sql, (self.conv_id,))

            if data:
                self.nombre_input.text = data[0][0]
                self.url_input.text = data[0][1]
                self.url_form_input.text = data[0][2]

        except Exception as e:
            print(f"Error al cargar datos de la convocatoria: {e}")

    def actualizar_convocatoria(self, instance):
        try:
            # Obtener los valores del formulario
            nuevo_nombre = self.nombre_input.text
            nueva_url = self.url_input.text
            nueva_url_form = self.url_form_input.text

            # Actualizar la convocatoria en la base de datos
            sql = """
                UPDATE ConvocatoriaActual
                SET nombre_convocatoria = ?, url_convocatoria = ?, url_forms = ?
                WHERE id_Convo = ?
            """
            execute_query(sql, (nuevo_nombre, nueva_url, nueva_url_form, self.conv_id))

            # Regresar a la pantalla anterior
            self.manager.current = 'scrn_content'

        except Exception as e:
            print(f"Error al actualizar la convocatoria: {e}")
