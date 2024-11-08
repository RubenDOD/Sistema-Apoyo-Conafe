import mysql.connector
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder

# Conexión a la base de datos
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="CONAFE"
)

# Cargar el archivo de diseño Kivy
Builder.load_file('main.kv')

class LoginScreen(BoxLayout):
    def verificar_credenciales(self):
        usuario = self.ids.txt_usuario.text
        contrasena = self.ids.txt_contrasena.text
        cursor = connection.cursor()
        consulta = "SELECT acceso FROM Usuario WHERE correo=%s AND password=%s"
        cursor.execute(consulta, (usuario, contrasena))
        resultado = cursor.fetchone()
        
        if resultado:
            acceso = resultado[0]
            self.ids.lbl_estado.text = "Login exitoso!"
            if acceso == 'Aspirante':
                App.get_running_app().root.current = 'aspirante'
            elif acceso == 'VistaDireccionTerritorial':
                App.get_running_app().root.current = 'vista_direccion_territorial'
            elif acceso == 'LEC':
                App.get_running_app().root.current = 'lec'
            elif acceso == 'Capacitador':
                App.get_running_app().root.current = 'capacitador'
        else:
            self.ids.lbl_estado.text = "Usuario o contraseña incorrectos."
        
        cursor.close()

class AspiranteScreen(BoxLayout):
    pass

class VistaDireccionTerritorialScreen(BoxLayout):
    pass

class LECScreen(BoxLayout):
    pass

class CapacitadorScreen(BoxLayout):
    pass

class LoginApp(App):
    def build(self):
        sm = ScreenManager()

        # Crear la pantalla de login y agregar el widget LoginScreen
        screen_login = Screen(name='login')
        screen_login.add_widget(LoginScreen())
        sm.add_widget(screen_login)

        # Crear la pantalla de aspirante y agregar el widget AspiranteScreen
        screen_aspirante = Screen(name='aspirante')
        screen_aspirante.add_widget(AspiranteScreen())
        sm.add_widget(screen_aspirante)

        # Crear la pantalla de VistaDireccionTerritorial y agregar el widget VistaDireccionTerritorialScreen
        screen_vdt = Screen(name='vista_direccion_territorial')
        screen_vdt.add_widget(VistaDireccionTerritorialScreen())
        sm.add_widget(screen_vdt)

        # Crear la pantalla de LEC y agregar el widget LECScreen
        screen_lec = Screen(name='lec')
        screen_lec.add_widget(LECScreen())
        sm.add_widget(screen_lec)

        # Crear la pantalla de capacitador y agregar el widget CapacitadorScreen
        screen_capacitador = Screen(name='capacitador')
        screen_capacitador.add_widget(CapacitadorScreen())
        sm.add_widget(screen_capacitador)

        return sm

if __name__ == '__main__':
    LoginApp().run()
