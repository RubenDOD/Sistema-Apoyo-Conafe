from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from admin import AdminWindow
from utils.datatable import DataTable

# Cargar ambos archivos .kv
Builder.load_file("general.kv")
Builder.load_file("admin.kv")

class MainScreen(Screen):
    def open_admin_window(self):
        admin_screen = Screen(name='admin')
        admin_screen.add_widget(AdminWindow())
        self.manager.add_widget(admin_screen)
        self.manager.current = 'admin'
    
    def open_button_screen(self):
        # Agregar la pantalla ButtonScreen con los botones A, B y C
        button_screen = ButtonScreen(name='button_screen')
        self.manager.add_widget(button_screen)
        self.manager.current = 'button_screen'

class ButtonScreen(Screen):
    pass

class InterfazConvocatoriasAspirante(Screen):
    def regresar(self):
        self.manager.current = 'VistaAspirante'

class InterfazCapacitaciones(Screen):
    def regresar(self):
        self.manager.current = 'VistaAspirante'

class InterfazConvocatoriasAdmin(Screen):
    def regresar(self):
        self.manager.current = 'VistaDireccionTerritorial'

class InterfazControlEscolarAdminTerritorial(Screen):
    pass

class InterfazCapacitacionesAdmin(Screen):
    def regresar(self):
        self.manager.current = 'VistaDireccionTerritorial'

class InterfazEstadisticas(Screen):
    def regresar(self):
        self.manager.current = 'VistaDireccionTerritorial'

class InterfazControlEscolar(Screen):
    def __init__(self, pantalla_regreso, **kwargs):
        super().__init__(**kwargs)
        self.pantalla_regreso = pantalla_regreso

    def regresar(self):
        self.manager.current = self.pantalla_regreso

class InterfazApoyos(Screen):
    def __init__(self, pantalla_regreso, **kwargs):
        super().__init__(**kwargs)
        self.pantalla_regreso = pantalla_regreso

    def regresar(self):
        self.manager.current = self.pantalla_regreso

class InterfazCapacitacionesTutor(Screen):
    def regresar(self):
        self.manager.current = 'VistaCapacitador'

class InterfazControlEscolarAdmin(Screen):
    def regresar(self):
        self.manager.current = 'VistaDireccionTerritorial'

class VistaAspirante(Screen):
    def convocatorias_aspirante(self):
        conv_Asp_screen = InterfazConvocatoriasAspirante(name='Interfaz_ConvocatoriasAspirante')
        self.manager.add_widget(conv_Asp_screen)
        self.manager.current = 'Interfaz_ConvocatoriasAspirante'
        
    def capacitaciones_aspirante(self):
        interfaz_capacitaciones_screen = InterfazCapacitaciones(name='Interfaz_Capacitaciones')
        self.manager.add_widget(interfaz_capacitaciones_screen)
        self.manager.current = 'Interfaz_Capacitaciones'

class VistaDireccionTerritorial(Screen):
    def convocatorias_DT(self):
        conv_admin_screen = InterfazConvocatoriasAdmin(name='Interfaz_ConvocatoriasAdmin')
        self.manager.add_widget(conv_admin_screen)
        self.manager.current = 'Interfaz_ConvocatoriasAdmin'
        
    def capacitacion_DT(self):
        interfaz_caps_admin_screen = InterfazCapacitacionesAdmin(name='Interfaz_CapacitacionesAdmin')
        self.manager.add_widget(interfaz_caps_admin_screen)
        self.manager.current = 'Interfaz_CapacitacionesAdmin'

    def controlEscolar_DT(self):
        conv_CE_admin_screen = InterfazControlEscolarAdmin(name='Interfaz_ControlEscolarAdmin')
        self.manager.add_widget(conv_CE_admin_screen)
        self.manager.current = 'Interfaz_ControlEscolarAdmin'
        
    def estadisticas_DT(self):
        interfaz_estadisticas_screen = InterfazEstadisticas(name='Interfaz_Estadisticas')
        self.manager.add_widget(interfaz_estadisticas_screen)
        self.manager.current = 'Interfaz_Estadisticas'

class VistaLEC(Screen):
    def controlEscolar_LEC(self):
        interfaz_controlEscolar_screen = InterfazControlEscolar(name='Interfaz_ControlEscolar', pantalla_regreso='VistaLEC')
        self.manager.add_widget(interfaz_controlEscolar_screen)
        self.manager.current = 'Interfaz_ControlEscolar'
        
    def apoyos_LEC(self):
        interfaz_apoyos_screen = InterfazApoyos(name='Interfaz_Apoyos', pantalla_regreso='VistaLEC')
        self.manager.add_widget(interfaz_apoyos_screen)
        self.manager.current = 'Interfaz_Apoyos'

class VistaCapacitador(Screen):
    def controlEscolar_LEC(self):
        interfaz_controlEscolar_screen = InterfazControlEscolar(name='Interfaz_ControlEscolar', pantalla_regreso='VistaCapacitador')
        self.manager.add_widget(interfaz_controlEscolar_screen)
        self.manager.current = 'Interfaz_ControlEscolar'
        
    def apoyos_LEC(self):
        interfaz_apoyos_screen = InterfazApoyos(name='Interfaz_Apoyos', pantalla_regreso='VistaCapacitador')
        self.manager.add_widget(interfaz_apoyos_screen)
        self.manager.current = 'Interfaz_Apoyos'
    
    def capacitaciones_tutor(self):
        interfaz_capacitacionesTutor_screen = InterfazCapacitacionesTutor(name='Interfaz_CapacitacionesTutor')
        self.manager.add_widget(interfaz_capacitacionesTutor_screen)
        self.manager.current = 'Interfaz_CapacitacionesTutor'

class MyApp(App):
    def __init__(self, start_screen='main', **kwargs):
        super().__init__(**kwargs)
        self.start_screen = start_screen  # Almacena la pantalla de inicio

    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(VistaAspirante(name='aspirante_screen'))
        sm.add_widget(VistaCapacitador(name='VistaCapacitador'))
        sm.add_widget(VistaLEC(name='VistaLEC'))  # Asegúrate de añadir VistaLEC al ScreenManager
        sm.current = self.start_screen  # Configura la pantalla inicial
        return sm

if __name__ == '__main__':
    # Cambia 'button_screen' a la pantalla que quieras abrir al inicio
    MyApp(start_screen='VistaCapacitador').run()