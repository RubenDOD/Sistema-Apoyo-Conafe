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
            if acceso == 'admin':
                App.get_running_app().root.current = 'admin'
            elif acceso == 'user':
                App.get_running_app().root.current = 'user'
        else:
            self.ids.lbl_estado.text = "Usuario o contraseña incorrectos."
        
        cursor.close()

class AdminScreen(BoxLayout):
    pass

class UserScreen(BoxLayout):
    pass

class LoginApp(App):
    def build(self):
        sm = ScreenManager()

        # Crear la pantalla de login y agregar el widget LoginScreen
        screen_login = Screen(name='login')
        screen_login.add_widget(LoginScreen())
        sm.add_widget(screen_login)

        # Crear la pantalla de admin y agregar el widget AdminScreen
        screen_admin = Screen(name='admin')
        screen_admin.add_widget(AdminScreen())
        sm.add_widget(screen_admin)

        # Crear la pantalla de usuario y agregar el widget UserScreen
        screen_user = Screen(name='user')
        screen_user.add_widget(UserScreen())
        sm.add_widget(screen_user)

        return sm

if __name__ == '__main__':
    LoginApp().run()

# Recuerde cambiar "your_password" y "your_database" por su contraseña y base de datos reales
