from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from collections import OrderedDict
from utils.datatable_capacitador import DataTableCapacitadorAspirante
from db_connection import execute_query


class CapacitadorAspiranteWindow(BoxLayout):
    def __init__(self, id_usuario, **kwargs):
        super().__init__(**kwargs)
        self.id_usuario = id_usuario
        print("ID desde el window:", id_usuario)
        content = self.ids.scrn_contents
        content.clear_widgets()
        aspirantes = self.get_info_aspirantes("General", id_usuario)
        aspirantesTable = DataTableCapacitadorAspirante(
            table=aspirantes, id_capacitador=self.id_usuario
        )
        content.add_widget(aspirantesTable)

    def get_info_aspirantes(self, mode, id_usuario):
        """Obtiene la información de los aspirantes desde la base de datos."""
        if mode == "General":
            _datosAspirante = OrderedDict({
                'id_Aspirante': {},
                'nombres': {},
                'fechaInicio': {},
                'fechaFinalizacion': {},
                'observaciones': {},
                'estadoCapacitacion': {},
                'apellidoPaterno': {},
                'apellidoMaterno': {},
            })

            query = """
            SELECT 
                ca.id_Aspirante,
                a.nombres AS nombre_aspirante,
                ca.fechaInicio,
                ca.fechaFinalizacion,
                ca.observaciones,
                ca.estadoCapacitacion,
                a.apellidoPaterno AS apellido_paterno,
                a.apellidoMaterno AS apellido_materno
            FROM 
                FII ca
            JOIN 
                Aspirante a ON ca.id_Aspirante = a.id_Aspirante
            WHERE 
                ca.id_Capacitador = ?
            """

            try:
                aspirantes = execute_query(query, (id_usuario,))
                for idx, user in enumerate(aspirantes):
                    _datosAspirante['id_Aspirante'][idx] = user[0]
                    _datosAspirante['nombres'][idx] = user[1]
                    _datosAspirante['fechaInicio'][idx] = user[2]
                    _datosAspirante['fechaFinalizacion'][idx] = user[3]
                    _datosAspirante['observaciones'][idx] = user[4]
                    _datosAspirante['estadoCapacitacion'][idx] = user[5]
                    _datosAspirante['apellidoPaterno'][idx] = user[6]
                    _datosAspirante['apellidoMaterno'][idx] = user[7]
                return _datosAspirante
            except Exception as e:
                print(f"Error al obtener los aspirantes: {e}")
                return _datosAspirante

    def go_back(self, instance):
        """Regresa a la pantalla principal."""
        if self.ids.scrn_mngr.current == 'scrn_content':
            App.get_running_app().root.current = 'capacitador'
        else:
            self.ids.scrn_mngr.current = 'scrn_content'


class ConvocatoriasApp(App):
    def build(self):
        return CapacitadorAspiranteWindow(id_usuario="example_id")

if __name__ == '__main__':
    ConvocatoriasApp().run()
