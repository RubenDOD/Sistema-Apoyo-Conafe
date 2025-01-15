from db_connection import execute_query
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
        """Redondea el valor al múltiplo de 100 más cercano, o a múltiplos de 10 si es menor a 300."""
        if value < 300:
            return max(10, round(value / 10) * 10)
        else:
            return max(100, round(value / 100) * 100)


    def fetch_and_calculate(self, units, state):
        """Busca los datos en la base de datos y realiza los cálculos."""
        try:
            # Consulta los datos del estado
            query = """
                SELECT 
                    CUERPO_CHICO, CUERPO_MEDIANO, CUERPO_GRANDE, 
                    CALZADO_H_MENOR, CALZADO_H_MEDIO, CALZADO_H_MAYOR, 
                    CALZADO_M_MENOR, CALZADO_M_MEDIO, CALZADO_M_MAYOR
                FROM tallasPromedio
                WHERE ESTADO = ?
            """
            row = execute_query(query, (state,))
            row = row[0]

            # Calcular tallas de cuerpo sin redondeo inicial
            tallas_cuerpo = [
                row[0] * units / 100,  # CUERPO_CHICO
                row[1] * units / 100,  # CUERPO_MEDIANO
                row[2] * units / 100,  # CUERPO_GRANDE
            ]
            cuerpo_total = sum(tallas_cuerpo)

            # Ajustar proporcionalmente si el total no coincide
            if cuerpo_total != units:
                factor = units / cuerpo_total
                tallas_cuerpo = [t * factor for t in tallas_cuerpo]

            # Redondear y ajustar al final para que la suma sea exacta
            tallas_cuerpo_redondeadas = [self.round_to_nearest_100(t) for t in tallas_cuerpo]
            diferencia = units - sum(tallas_cuerpo_redondeadas)
            if diferencia != 0:
                tallas_cuerpo_redondeadas[0] += diferencia  # Ajustar en la primera categoría

            # Distribuir calzado: 48% hombres, 52% mujeres
            calzado_total = units
            calzado_hombres = calzado_total * 0.48
            calzado_mujeres = calzado_total * 0.52

            # Calcular calzado sin redondeo inicial
            calzado_h = [
                row[3] * calzado_hombres / 100,  # CALZADO_H_MENOR
                row[4] * calzado_hombres / 100,  # CALZADO_H_MEDIO
                row[5] * calzado_hombres / 100,  # CALZADO_H_MAYOR
            ]
            calzado_m = [
                row[6] * calzado_mujeres / 100,  # CALZADO_M_MENOR
                row[7] * calzado_mujeres / 100,  # CALZADO_M_MEDIO
                row[8] * calzado_mujeres / 100,  # CALZADO_M_MAYOR
            ]

            # Ajustar proporcionalmente si los totales no coinciden
            if sum(calzado_h) != calzado_hombres:
                factor_h = calzado_hombres / sum(calzado_h)
                calzado_h = [t * factor_h for t in calzado_h]

            if sum(calzado_m) != calzado_mujeres:
                factor_m = calzado_mujeres / sum(calzado_m)
                calzado_m = [t * factor_m for t in calzado_m]

            # Redondear y ajustar al final para que las sumas sean exactas
            calzado_h_redondeado = [self.round_to_nearest_100(t) for t in calzado_h]
            calzado_m_redondeado = [self.round_to_nearest_100(t) for t in calzado_m]

            diferencia_h = calzado_hombres - sum(calzado_h_redondeado)
            diferencia_m = calzado_mujeres - sum(calzado_m_redondeado)

            if diferencia_h != 0:
                calzado_h_redondeado[0] += diferencia_h  # Ajustar en la primera categoría
            if diferencia_m != 0:
                calzado_m_redondeado[0] += diferencia_m  # Ajustar en la primera categoría

            # Organizar resultados
            result_text = (
                "Se recomienda comprar:\n\n"
                "Tallas Pantalón/Camisa:\n"
                f"Chicas: {tallas_cuerpo_redondeadas[0]}\n"
                f"Medianas: {tallas_cuerpo_redondeadas[1]}\n"
                f"Grandes: {tallas_cuerpo_redondeadas[2]}\n\n"
                "Calzado:\n"
                "Hombres:\n"
                f"Tallas chicas (-26): {calzado_h_redondeado[0]}\n"
                f"Tallas medianas (26-28): {calzado_h_redondeado[1]}\n"
                f"Tallas grandes (28+): {calzado_h_redondeado[2]}\n\n"
                "Mujeres:\n"
                f"Tallas chicas (-23): {calzado_m_redondeado[0]}\n"
                f"Tallas medianas (23-25): {calzado_m_redondeado[1]}\n"
                f"Tallas grandes (25+): {calzado_m_redondeado[2]}\n\n"
                "Datos redondeados a múltiplos de 100 unidades para valores de 300 unidades en adelante."
            )

            return result_text

        except Exception as err:
            return f"Error al realizar los cálculos: {err}"


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