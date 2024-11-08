import re
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

class CustomBoxLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(CustomBoxLayout, self).__init__(**kwargs)
        self.orientation = 'vertical'
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.06, 0.52, 0.52, 1)  # Fondo color teal oscuro
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class LoginScreen(CustomBoxLayout):
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
            
            app = App.get_running_app()
            sm = app.root  # Accede al ScreenManager principal
            
            # Seleccionar pantalla según el rol
            if acceso == 'Aspirante':
                sm.current = 'aspirante'
            elif acceso == 'Miembro Dirección Territorial':
                sm.current = 'vista_direccion_territorial'
            elif acceso == 'LEC':
                sm.current = 'lec'
            elif acceso == 'Capacitador':
                sm.current = 'capacitador'
        else:
            self.ids.lbl_estado.text = "Usuario o contraseña incorrectos."
        
        cursor.close()

    def go_to_register(self):
        App.get_running_app().root.current = 'register'
    
    def limpiar_campos(self):
        """Limpia los campos de texto cuando se regresa al login."""
        self.ids.txt_usuario.text = ""
        self.ids.txt_contrasena.text = ""
        self.ids.lbl_estado.text = ""

class RegisterScreen(CustomBoxLayout):
    def registrar_usuario(self):
        usuario = self.ids.txt_usuario.text
        contrasena = self.ids.txt_contrasena.text
        rol = self.ids.spinner_rol.text
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", usuario):
            self.ids.lbl_estado.text = "Por favor ingresa un correo electrónico válido."
            return
        
        if len(contrasena) < 8:
            self.ids.lbl_estado.text = "La contraseña debe tener al menos 8 caracteres."
            return
        
        if rol == 'Seleccionar rol':
            self.ids.lbl_estado.text = "Por favor selecciona un rol."
            return

        if rol == 'Miembro Dirección Territorial' and not usuario.endswith("@conafe.gob.mx"):
            self.ids.lbl_estado.text = "El correo debe tener la terminación @conafe.gob.mx para este rol."
            return

        cursor = connection.cursor()
        consulta_verificacion = "SELECT * FROM Usuario WHERE correo=%s"
        cursor.execute(consulta_verificacion, (usuario,))
        resultado = cursor.fetchone()
        
        if resultado:
            self.ids.lbl_estado.text = "El usuario ya está registrado."
            cursor.close()
            return

        consulta_registro = "INSERT INTO Usuario (correo, password, acceso) VALUES (%s, %s, %s)"
        cursor.execute(consulta_registro, (usuario, contrasena, rol))
        connection.commit()
        cursor.close()
        
        self.ids.lbl_estado.text = "Registro exitoso. Ahora puedes iniciar sesión."
        App.get_running_app().root.current = 'login'

    def go_back(self):
        App.get_running_app().root.current = 'login'

class AspiranteScreen(CustomBoxLayout):
    pass

class VistaDireccionTerritorialScreen(CustomBoxLayout):
    pass

class LECScreen(CustomBoxLayout):
    pass

class CapacitadorScreen(CustomBoxLayout):
    pass

class LoginApp(App):
    def build(self):
        sm = ScreenManager()

        screen_login = Screen(name='login')
        screen_login.add_widget(LoginScreen())
        sm.add_widget(screen_login)

        screen_register = Screen(name='register')
        screen_register.add_widget(RegisterScreen())
        sm.add_widget(screen_register)

        screen_aspirante = Screen(name='aspirante')
        screen_aspirante.add_widget(AspiranteScreen())
        sm.add_widget(screen_aspirante)

        screen_vdt = Screen(name='vista_direccion_territorial')
        screen_vdt.add_widget(VistaDireccionTerritorialScreen())
        sm.add_widget(screen_vdt)

        screen_lec = Screen(name='lec')
        screen_lec.add_widget(LECScreen())
        sm.add_widget(screen_lec)

        screen_capacitador = Screen(name='capacitador')
        screen_capacitador.add_widget(CapacitadorScreen())
        sm.add_widget(screen_capacitador)

        return sm

if __name__ == '__main__':
    LoginApp().run()
