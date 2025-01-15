import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
import pyodbc
from kivy.graphics import Color, Rectangle

# Datos de la base de datos de Azure
server = 'conafe-server.database.windows.net'
database = 'conafe-database'
username = 'admin-conafe'
password = 'MateriaAcaba08/01/25'
driver = '{ODBC Driver 17 for SQL Server}'

def obtener_beneficiarios():
    """Consulta a la base de datos para obtener el padrón de becas."""
    try:
        connection = pyodbc.connect(
            f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}'
        )
        cursor = connection.cursor()
        cursor.execute('SELECT claveApoyo, tipo_apoyo FROM apoyo_economico')
        rows = cursor.fetchall()
        cursor.close()
        connection.close()

        beneficiarios = [{'Estudiante': row[0], 'Beca': row[1]} for row in rows]
        return beneficiarios
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return []

class PadronBecasScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Layout principal
        self.layout = BoxLayout(orientation='vertical')
        with self.layout.canvas.before:
            Color(0.06, 0.52, 0.52, 1)  # Establecer color de fondo
            self.rect = Rectangle(size=self.layout.size, pos=self.layout.pos)
            self.layout.bind(size=self._update_rect, pos=self._update_rect)
        
        self.add_widget(self.layout)

        # Etiqueta para mostrar los datos
        self.label = Label(text="Padrón Vacio", size_hint=(1, 0.8))
        self.layout.add_widget(self.label)

        # Botón para recargar datos
        btn_actualizar = Button(text="Actualizar Padrón", size_hint=(1, 0.1), background_color=(0.1, 0.6, 0.9, 1))
        btn_actualizar.bind(on_release=self.actualizar_padron)
        self.layout.add_widget(btn_actualizar)

        # Botón para regresar
        btn_volver = Button(text="Volver", size_hint=(1, 0.1), background_color=(0.1, 0.6, 0.9, 1))
        btn_volver.bind(on_release=self.volver)
        self.layout.add_widget(btn_volver)

    def actualizar_padron(self, _):
        """Consulta los datos y actualiza la etiqueta."""
        beneficiarios = obtener_beneficiarios()
        if beneficiarios:
            texto = "Padrón de Becas:\n\n"
            for b in beneficiarios:
                texto += f"Estudiante: {b['Estudiante']}, Beca: {b['Beca']}\n"
        else:
            texto = "No hay datos disponibles o ocurrió un error."

        self.label.text = texto

    def volver(self, _):
        """Regresa a la pantalla anterior."""
        self.label.text = "Padrón Vacío"
        App.get_running_app().root.current = 'vista_direccion_territorial'

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

""" class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(PadronBecasScreen(name='padron_becas'))
        # Aquí se puede agregar la pantalla 'vista_direccion_territorial' con su propia implementación
        return sm 

if __name__ == "__main__":
    MyApp().run() """

class PadronBecasApp(App): 
    def build(self): 
        sm = ScreenManager() 
        sm.add_widget(PadronBecasScreen(name='padron_becas')) 
        return sm
