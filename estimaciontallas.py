import mysql.connector
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.label import Label


class EstimacionTallasScreen(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dropdown = DropDown()
        self.selected_state = None

        # Lista de estados
        states = ['Durango', 'Campeche']

        # Agregar opciones al Dropdown
        for state in states:
            btn = Button(text=state, size_hint_y=None, height=40, background_color=(1, 1, 1, 1), color=(1, 1, 1, 1))
            btn.bind(on_release=lambda btn: self.set_state(btn.text))
            self.dropdown.add_widget(btn)

    def set_state(self, state):
        """Actualiza el estado seleccionado y cierra el dropdown."""
        self.selected_state = state
        self.ids.state_button.text = state
        self.dropdown.dismiss()

    def on_accept(self):
        """Acción al presionar el botón 'Aceptar'."""
        units = self.ids.units_input.text
        if units.isdigit() and self.selected_state:
            units = int(units)
            results = self.fetch_and_calculate(units, self.selected_state)
            self.show_popup("Resultados", results)
        else:
            self.show_popup("Error", "Por favor, complete ambos campos correctamente.")

    def round_to_nearest_100(self, value):
        """Redondea el valor al múltiplo de 100 más cercano, con un mínimo de 100."""
        return max(100, round(value / 100) * 100)

    def fetch_and_calculate(self, units, state):
        """Busca los datos en la base de datos y realiza los cálculos."""
        try:
            # Conexión a la base de datos
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                passwd='1234',
                database='CONAFE'
            )
            cursor = conn.cursor(dictionary=True)
            
            # Consulta los datos del estado
            query = f"""
                SELECT 
                    CUERPO_CHICO, CUERPO_MEDIANO, CUERPO_GRANDE, 
                    CALZADO_H_MENOR, CALZADO_H_MEDIO, CALZADO_H_MAYOR, 
                    CALZADO_M_MENOR, CALZADO_M_MEDIO, CALZADO_M_MAYOR
                FROM tallasPromedio
                WHERE ESTADO = %s
            """
            cursor.execute(query, (state,))
            row = cursor.fetchone()

            if not row:
                return "No se encontraron datos para el estado seleccionado."

            # Calcular tallas de cuerpo
            resultados = {
                "CUERPO_CHICO": self.round_to_nearest_100(row["CUERPO_CHICO"] * units / 100),
                "CUERPO_MEDIANO": self.round_to_nearest_100(row["CUERPO_MEDIANO"] * units / 100),
                "CUERPO_GRANDE": self.round_to_nearest_100(row["CUERPO_GRANDE"] * units / 100),
            }

            # Distribuir calzado: 48% hombres, 52% mujeres
            calzado_total = units
            calzado_hombres = calzado_total * 0.48
            calzado_mujeres = calzado_total * 0.52

            resultados.update({
                "CALZADO_H_MENOR": self.round_to_nearest_100(row["CALZADO_H_MENOR"] * calzado_hombres / 100),
                "CALZADO_H_MEDIO": self.round_to_nearest_100(row["CALZADO_H_MEDIO"] * calzado_hombres / 100),
                "CALZADO_H_MAYOR": self.round_to_nearest_100(row["CALZADO_H_MAYOR"] * calzado_hombres / 100),
                "CALZADO_M_MENOR": self.round_to_nearest_100(row["CALZADO_M_MENOR"] * calzado_mujeres / 100),
                "CALZADO_M_MEDIO": self.round_to_nearest_100(row["CALZADO_M_MEDIO"] * calzado_mujeres / 100),
                "CALZADO_M_MAYOR": self.round_to_nearest_100(row["CALZADO_M_MAYOR"] * calzado_mujeres / 100),
            })

            # Organiza los resultados
            result_text = (
                "Se recomienda comprar:\n\n"
                "Tallas Pantalón/Camisa:\n"
                f"Chicas: {resultados['CUERPO_CHICO']}\n"
                f"Medianas: {resultados['CUERPO_MEDIANO']}\n"
                f"Grandes: {resultados['CUERPO_GRANDE']}\n\n"
                "Calzado:\n"
                "Hombres:\n"
                f"Tallas chicas (-26): {resultados['CALZADO_H_MENOR']}\n"
                f"Tallas medianas (26-28): {resultados['CALZADO_H_MEDIO']}\n"
                f"Tallas grandes (28+): {resultados['CALZADO_H_MAYOR']}\n\n"
                "Mujeres:\n"
                f"Tallas chicas (-23): {resultados['CALZADO_M_MENOR']}\n"
                f"Tallas medianas (23-25): {resultados['CALZADO_M_MEDIO']}\n"
                f"Tallas grandes (25+): {resultados['CALZADO_M_MAYOR']}\n\n"
                "Datos redondeados a múltiplos de 100 unidades."
            )

            return result_text

        except mysql.connector.Error as err:
            return f"Error al conectar a la base de datos: {err}"
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def show_popup(self, title, message):
        """Muestra un popup con el mensaje proporcionado."""
        popup = Popup(title=title,
                      content=Label(text=message, text_size=(400, None), halign='left'),
                      size_hint=(0.8, 0.6),
                      auto_dismiss=True)
        popup.open()


class EstimacionTallasApp(App):
    def build(self):
        return EstimacionTallasScreen()


if __name__ == '__main__':
    EstimacionTallasApp().run()
