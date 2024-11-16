from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
import mysql.connector
import io
from kivy.lang import Builder

#Builder.load_file('FII.kv')

class MySQLConnection:
    def __init__(self):
        # Conectar a la base de datos MySQL
        self.conn = mysql.connector.connect(
            host="localhost",  # Cambia según tu configuración
            user="root",  # Cambia según tu configuración
            password="1234",  # Cambia según tu configuración
            database="conafe"  # Cambia según tu configuración
        )
        self.cursor = self.conn.cursor()

    def fetch_data(self, clavecct=None):
        # Obtener los registros de la tabla con filtro opcional en id_CCT
        if clavecct:
            query = "SELECT * FROM fii WHERE id_CCT = %s"
            self.cursor.execute(query, (clavecct,))
        else:
            query = "SELECT * FROM fii"
            self.cursor.execute(query)
        return self.cursor.fetchall()

    def close_connection(self):
        # Cierra la conexión a la base de datos
        self.cursor.close()
        self.conn.close()

class MainWidget(BoxLayout):
    def regresar_a_tablero(self):
        app = App.get_running_app()
        app.root.current = 'tablero de control'  # Cambia 'tablero_control' por el nombre exacto de tu pantalla de Tablero de Control

    def on_kv_post(self, base_widget):
        # Cargar los datos solo si no se han cargado previamente
        if not hasattr(self, '_tabla_cargada'):
            self.actualizar_tabla()
            self._tabla_cargada = True  # Marca que la tabla ya ha sido cargada

    def actualizar_tabla(self, clavecct=None):
        # Limpiar el layout de la tabla antes de actualizar
        table_layout = self.ids.table_layout
        table_layout.clear_widgets()

        # Conectar a la base de datos y obtener los datos
        db = MySQLConnection()
        data = db.fetch_data(clavecct=clavecct)
        db.close_connection()

        # Encabezados de la tabla
        headers = ["id_Capacitador", "id_Aspirante", "ClaveCCT", "EstadoCapacitacion", "fechaInicio", "fechaFinalizacion",
                   "Observaciones"]

        # Agregar encabezados
        for header in headers:
            header_label = Label(text=header, bold=True, size_hint_x=None, width=150, font_size="16sp",
                                 color=(0.2, 0.6, 0.8, 1))
            table_layout.add_widget(header_label)

        # Si no se encuentran datos, mostrar mensaje de error
        if not data:
            self.mostrar_popup("No se encontraron datos para la ClaveCCT proporcionada.")
            self.ids.export_button.disabled = True
            return
        else:
            # Si se encuentran datos, habilitar el botón de exportación
            self.ids.export_button.disabled = False

        # Guardar los datos encontrados en un atributo para exportación, incluyendo encabezados
        self.filtered_data = [headers] + data

        # Agregar cada fila de datos
        for row in data:
            for cell in row:
                label = Label(
                    text=str(cell),
                    size_hint_x=None,
                    width=150,
                    font_size="14sp",
                    color=(0, 0, 0, 1)
                )
                table_layout.add_widget(label)

    def filtrar_por_clavecct(self, clavecct_text):
        # Verificar si se ingresó un valor en clavecct_text
        if clavecct_text.isdigit():  # Solo procesa si es un entero
            clavecct = int(clavecct_text)
            self.actualizar_tabla(clavecct=clavecct)
        else:
            # Mostrar todos los datos si no hay filtro válido
            self.actualizar_tabla()

    def mostrar_popup(self, mensaje):
        # Mostrar un popup de error
        popup = Popup(title="Error",
                      content=Label(text=mensaje),
                      size_hint=(0.6, 0.4))
        popup.open()

    def exportar_datos(self):
        # Exportar los datos filtrados a un archivo .txt, incluyendo encabezados
        if hasattr(self, 'filtered_data') and self.filtered_data:
            with io.open("Reporte_FII.txt", "w", encoding="utf-8") as file:
                file.write("Registros Exportados:\n\n")
                # Escribir cada fila (encabezados y datos)
                for row in self.filtered_data:
                    file.write("\t".join(str(cell) for cell in row) + "\n")
            self.mostrar_popup("Datos exportados a Reporte_FII.txt correctamente.")
        else:
            self.mostrar_popup("No hay datos para exportar.")


class FIIApp(App):
    def build(self):
        return MainWidget()

if __name__ == "__main__":
    FIIApp().run()
