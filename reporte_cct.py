import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.popup import Popup
import pandas as pd
from fpdf import FPDF
import pyodbc
from kivy.graphics import Color, Rectangle

# Conexión a la base de datos de Azure
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=conafe-server.database.windows.net;"
    "DATABASE=conafe-database;"
    "UID=admin-conafe;"
    "PWD=MateriaAcaba08/01/25"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Función para obtener IDs de CCT desde la base de datos
def obtener_ids_cct():
    query = "SELECT claveCentro FROM CCT"
    cursor.execute(query)
    rows = cursor.fetchall()
    return [row.claveCentro for row in rows]

# Función para obtener datos de educadores desde la base de datos
def obtener_educadores(claveCentro):
    query = """ SELECT claveCentro, nombre, estado, codigoPostal, municipio, localidad, nivelEducativo, turno, cupos_disponibles, latitud, longitud 
    FROM CCT 
    WHERE claveCentro = ? """
    cursor.execute(query, claveCentro)
    rows = cursor.fetchall()
    return [dict(zip([column[0] for column in cursor.description], row)) for row in rows]

# Función para generar reporte en Excel
def generar_reporte_excel(claveCentro):
    try:
        educadores = obtener_educadores(claveCentro)
        df = pd.DataFrame(educadores)
        if df.empty:
            print(f"No se encontraron datos para el CCT claveCentro: {claveCentro}")
            return
        file_name = f"reporte_{claveCentro}.xlsx"
        df.to_excel(file_name, index=False)
        print(f"Reporte Excel generado: {file_name}")
        mostrar_popup("Reporte Excel generado", f"Reporte Excel generado: {file_name}") 
    except Exception as e:
        print(f"Error al generar el reporte Excel: {e}")

# Función para generar reporte en PDF
def generar_reporte_pdf(claveCentro):
    try:
        educadores = obtener_educadores(claveCentro)
        if not educadores:
            print(f"No se encontraron datos para el CCT claveCentro: {claveCentro}")
            return
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Reporte de Educadores para CCT claveCentro: {claveCentro}", ln=True, align='C')
        pdf.ln(10)
        for educador in educadores:
            for key, value in educador.items():
                pdf.cell(0, 10, txt=f"{key}: {value}", ln=True)
            pdf.ln(5)
        file_name = f"reporte_{claveCentro}.pdf"
        pdf.output(file_name)
        print(f"Reporte PDF generado: {file_name}")
        mostrar_popup("Reporte PDF generado", f"Reporte PDF generado: {file_name}")
    except Exception as e:
        print(f"Error al generar el reporte PDF: {e}")

# Función para mostrar un Popup 
def mostrar_popup(titulo, mensaje): 
    layout = BoxLayout(orientation='vertical', padding=10) 
    mensaje_label = Label(text=mensaje) 
    cerrar_button = Button(text="Cerrar", size_hint=(1, 0.3)) 
    layout.add_widget(mensaje_label) 
    layout.add_widget(cerrar_button) 
    
    popup = Popup(title=titulo, content=layout, size_hint=(0.8, 0.4)) 
    cerrar_button.bind(on_press=popup.dismiss) 
    popup.open()

# Interfaz de usuario con Kivy
class ReporteCCTScreen(Screen):
    def __init__(self, **kwargs): 
        super().__init__(**kwargs) 
        self.add_widget(self.build())

    def build(self):
        root = BoxLayout(orientation='vertical')
        with root.canvas.before:
            Color(0.06, 0.52, 0.52, 1)  # Establecer color de fondo
            self.rect = Rectangle(size=root.size, pos=root.pos)
            root.bind(size=self._update_rect, pos=self._update_rect)
        
        self.label = Label(text="Bienvenido al sistema de gestión de CCTs")
        root.add_widget(self.label)
        
        self.spinner_label = Label(text="Seleccione el ID del CCT:")
        root.add_widget(self.spinner_label)
        
        self.spinner = Spinner(text='Seleccione',
                               values=obtener_ids_cct(),
                               color=(0, 0, 0, 1))
        root.add_widget(self.spinner)
        
        self.report_format_label = Label(text="Seleccione el formato del reporte:")
        root.add_widget(self.report_format_label)
        
        self.excel_button = Button(text="Excel", background_color=(0.1, 0.6, 0.9, 1))
        self.excel_button.bind(on_press=self.generate_excel_report)
        root.add_widget(self.excel_button)
        
        self.pdf_button = Button(text="PDF", background_color=(0.1, 0.6, 0.9, 1))
        self.pdf_button.bind(on_press=self.generate_pdf_report)
        root.add_widget(self.pdf_button)

        self.volver_button = Button(text="Volver", background_color=(0.1, 0.6, 0.9, 1))
        self.volver_button.bind(on_press=self.volver_menu)
        root.add_widget(self.volver_button)
        
        return root
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def generate_excel_report(self, instance):
        claveCentro = self.spinner.text
        generar_reporte_excel(claveCentro)
    
    def generate_pdf_report(self, instance):
        claveCentro = self.spinner.text
        generar_reporte_pdf(claveCentro)

    def volver_menu(self, instance):
        self.spinner.text = 'Seleccione'
        app = App.get_running_app() 
        app.root.current = 'vista_direccion_territorial'

