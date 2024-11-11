from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
import mysql.connector
from mysql.connector import Error

class DatabaseManager:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host='127.0.0.1',       
                database='CONAFE',    
                user='root',            
                password='35283447'     
            )
            if self.connection.is_connected():
                print("Conexión exitosa a la base de datos")
        except Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            self.connection = None

    def get_convocatorias(self):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT id_Convo, nombre_convocatoria, estado_convocatoria FROM ConvocatoriaActual")
            return cursor.fetchall() 
        except Error as e:
            print(f"Error al obtener convocatorias: {e}")
            return []  

    def publicar_convocatoria(self, id_convocatoria):
        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE ConvocatoriaActual SET estado_convocatoria = 'Publicada' WHERE id_Convo = %s", (id_convocatoria,))
            self.connection.commit()
            print("Convocatoria publicada correctamente")
        except Error as e:
            print(f"Error al actualizar convocatoria: {e}")

# Pantalla de Login
class LoginScreen(Screen):
    def validar_credenciales(self):
        usuario = self.ids.input_usuario.text
        contrasena = self.ids.input_contrasena.text
        
        db_manager = DatabaseManager()
        
        try:
            cursor = db_manager.connection.cursor(dictionary=True)
            query = "SELECT * FROM Usuario WHERE correo = %s AND password = %s"
            cursor.execute(query, (usuario, contrasena))
            resultado = cursor.fetchone()
            
            if resultado: 
                self.manager.current = "main" #"main--------------------------" 
            else:
                self.mostrar_mensaje("Usuario o contraseña incorrectos.")
        
        except Error as e:
            print(f"Error al validar usuario: {e}")
            self.mostrar_mensaje("Error al conectar con la base de datos.")
        
        finally:
            if cursor:
                cursor.close()
    
    def mostrar_mensaje(self, mensaje):
        popup = Popup(title="Error de autenticación",
                      content=Label(text=mensaje),
                      size_hint=(0.8, 0.4))
        popup.open()

# Pantalla principal
class MainScreen(Screen):
    def on_pre_enter(self):
        db_manager = DatabaseManager()
        convocatorias = db_manager.get_convocatorias()
        
        if convocatorias:
            self.ids.spinner_convocatorias.values = [
                f"{c['id_Convo']}: {c['nombre_convocatoria']} ({c['estado_convocatoria']})"
                for c in convocatorias
            ]
        else:
            self.ids.spinner_convocatorias.values = ['No hay convocatorias disponibles']

kv = Builder.load_file("interfaz.kv")

class InterfazApp(App):
    def build(self):
        return kv

    def publicar_convocatoria(self, instance):
        main_screen = self.root.get_screen('main')
        seleccion = main_screen.ids.spinner_convocatorias.text
        
        if seleccion == 'Selecciona convocatoria':
            self.mostrar_mensaje_error("Por favor, selecciona una convocatoria.")
            return

        id_convocatoria = int(seleccion.split(':')[0])
        db_manager = DatabaseManager()
        convocatoria = next((c for c in db_manager.get_convocatorias() if c['id_Convo'] == id_convocatoria), None)

        if convocatoria:
            if convocatoria['estado_convocatoria'] == 'Aprobada':
                db_manager.publicar_convocatoria(id_convocatoria)
                main_screen.on_pre_enter()
                self.mostrar_mensaje_exito("Convocatoria publicada con éxito.")
            else:
                self.mostrar_mensaje_error("La convocatoria no ha sido aprobada aún. Seleccione otra.")
        else:
            self.mostrar_mensaje_error("Error al encontrar la convocatoria seleccionada.")

    def mostrar_mensaje_error(self, mensaje):
        popup = Popup(title="Error", content=Label(text=mensaje), size_hint=(0.8, 0.4))
        popup.open()

    def mostrar_mensaje_exito(self, mensaje):
        popup = Popup(title="Éxito", content=Label(text=mensaje), size_hint=(0.8, 0.4))
        popup.open()

if __name__ == '__main__':
    InterfazApp().run()
