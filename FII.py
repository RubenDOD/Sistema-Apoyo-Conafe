from db_connection import execute_query
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
import io
from kivy.lang import Builder

#Builder.load_file('FII.kv')

class MainWidget(BoxLayout):
    def regresar_a_tablero(self):
        app = App.get_running_app()
        app.root.current = 'tablero de control'  # Cambia 'tablero_control' por el nombre exacto de tu pantalla de Tablero de Control

    def on_kv_post(self, base_widget):
        if not hasattr(self, '_tabla_cargada'):
            self.actualizar_tabla()
            self._tabla_cargada = True

    def actualizar_tabla(self, clavecct=None):
        table_layout = self.ids.table_layout
        table_layout.clear_widgets()

        query = "SELECT * FROM fii"
        params = ()
        if clavecct:
            query += " WHERE id_CCT = ?"
            params = (clavecct,)

        data = execute_query(query, params)

        headers = ["id_Capacitador", "id_Aspirante", "ClaveCCT", "EstadoCapacitacion", "fechaInicio", "fechaFinalizacion", "Observaciones"]

        for header in headers:
            header_label = Label(text=header, bold=True, size_hint_x=None, width=150, font_size="16sp", color=(0.2, 0.6, 0.8, 1))
            table_layout.add_widget(header_label)

        if not data:
            self.mostrar_popup("No se encontraron datos para la ClaveCCT proporcionada.")
            self.ids.export_button.disabled = True
            return
        else:
            self.ids.export_button.disabled = False

        self.filtered_data = [headers] + data

        for row in data:
            for cell in row:
                label = Label(text=str(cell), size_hint_x=None, width=150, font_size="14sp", color=(0, 0, 0, 1))
                table_layout.add_widget(label)

    def filtrar_por_clavecct(self, clavecct_text):
        if clavecct_text.isdigit():
            clavecct = int(clavecct_text)
            self.actualizar_tabla(clavecct=clavecct)
        else:
            self.actualizar_tabla()

    def mostrar_popup(self, mensaje):
        popup = Popup(title="Error", content=Label(text=mensaje), size_hint=(0.6, 0.4))
        popup.open()

    def exportar_datos(self):
        if hasattr(self, 'filtered_data') and self.filtered_data:
            with io.open("Reporte_FII.txt", "w", encoding="utf-8") as file:
                file.write("Registros Exportados:\n\n")
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