from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from collections import OrderedDict
from utils.datatable_convocatorias import DataTableConv
from datetime import datetime
import hashlib
from añadir_convocatoria import AddConvoScreen
from kivy.uix.boxlayout import BoxLayout
import webbrowser
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from admin import AdminWindow
from kivy.properties import StringProperty
from utils.datatable_capacitador import DataTableCapacitadorAspirante
from db_connection import execute_query

class CapacitadorAspiranteWindow(BoxLayout):
    # id_usuario = StringProperty()
    def __init__(self, id_usuario, **kwargs):
        super().__init__(**kwargs)
        self.id_usuario = id_usuario
        # Builder.load_file("capacitador_aspirante.kv")  # Carga explícita de admin.kv

        print("id desde el window", id_usuario)
        content = self.ids.scrn_contents
        content.clear_widgets()
        aspirantes = self.get_info_aspirantes("General", id_usuario)
        aspirantesTable = DataTableCapacitadorAspirante(table=aspirantes, id_capacitador=self.id_usuario)  # Pasa button_callback aqui
        content.add_widget(aspirantesTable)

    def get_info_aspirantes(self, mode, id_usuario):
        print("id dentro de la consulta ", id_usuario)

        if mode == "General":
            _datosAspirante = OrderedDict()
            _datosAspirante['id_Aspirante'] = {}
            _datosAspirante['nombres'] = {}
            _datosAspirante['fechaInicio'] = {}
            _datosAspirante['fechaFinalizacion'] = {}
            _datosAspirante['observaciones'] = {}
            _datosAspirante['estadoCapacitacion'] = {}
            _datosAspirante['apellidoPaterno'] = {}
            _datosAspirante['apellidoMaterno'] = {}

            ids = []
            nombres = []
            fechasInicio = []
            fechasFinal = []
            observaciones = []
            status = []
            aPaterno = []  
            aMaterno = []

            print("Entra a la consulta")
            sql = """
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
        
            aspirantes = execute_query(sql, (id_usuario,))

            for user in aspirantes:
                ids.append(user[0])
                nombres.append(user[1])
                fechasInicio.append(user[2])
                fechasFinal.append(user[3])
                observaciones.append(user[4])
                status.append(user[5])
                aPaterno.append(user[6])
                aMaterno.append(user[7])

            users_length = len(nombres)
            print("numero de aspirantes: ", users_length)
            idx = 0
            while idx < users_length:
                _datosAspirante['id_Aspirante'][idx] = ids[idx]
                _datosAspirante['nombres'][idx] = nombres[idx]
                _datosAspirante['fechaInicio'][idx] = fechasInicio[idx]
                _datosAspirante['fechaFinalizacion'][idx] = fechasFinal[idx]
                _datosAspirante['observaciones'][idx] = observaciones[idx]
                _datosAspirante['estadoCapacitacion'][idx] = status[idx]
                _datosAspirante['apellidoPaterno'][idx] = aPaterno[idx]
                _datosAspirante['apellidoMaterno'][idx] = aMaterno[idx]
                idx += 1

            return _datosAspirante
    
    def go_back(self, instance):
        # Verifica si la pantalla actual es la pantalla inicial
        if self.ids.scrn_mngr.current == 'scrn_content':  # 'scrn_content' como la pantalla principal
            # Si estamos en la pantalla inicial, regresa a VistaDireccionTerritorialScreen
            App.get_running_app().root.current = 'capacitador'
        else:
            # Si no estamos en la pantalla inicial, vuelve a la pantalla anterior dentro de ConvocatoriaWindow
            self.ids.scrn_mngr.current = 'scrn_content'

class ConvocatoriasApp(App):
    def build(self):
        return CapacitadorAspiranteWindow()

if __name__=='__main__':
    ConvocatoriasApp().run()