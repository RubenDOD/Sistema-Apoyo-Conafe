from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from tkinter import Tk
from tkinter.filedialog import askopenfilename

kv = Builder.load_file("interfaz.kv")

class InterfazApp(App):
    def build(self):
        return kv

    def mostrar_popup_url(self):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        url_input = TextInput(hint_text="Ingresa la URL de la convocatoria", multiline=False)
        content.add_widget(url_input)
        
        boton_aceptar = Button(text="Aceptar", size_hint_y=None, height=40)
        content.add_widget(boton_aceptar)

        popup = Popup(title="Referencia de la convocatoria",
                      content=content,
                      size_hint=(0.8, 0.4))
        
        def aceptar_url(instance):
            url = url_input.text
            print(f"URL ingresada: {url}")
            popup.dismiss()

        boton_aceptar.bind(on_press=aceptar_url)
        popup.open()

    def seleccionar_archivo_pdf(self):
        root = Tk()
        root.withdraw()  
        root.call('wm', 'attributes', '.', '-topmost', True)  
        
        archivo_seleccionado = askopenfilename(
            title="Seleccionar Archivo PDF",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        
        if archivo_seleccionado:
            print(f"Archivo seleccionado: {archivo_seleccionado}")
            self.mostrar_popup_confirmacion(archivo_seleccionado)

    def mostrar_popup_confirmacion(self, archivo_nombre):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        label_confirmacion = TextInput(text=f"Archivo seleccionado: {archivo_nombre}", readonly=True)
        content.add_widget(label_confirmacion)
        
        boton_aceptar = Button(text="Aceptar", size_hint_y=None, height=40)
        content.add_widget(boton_aceptar)

        popup = Popup(title="Confirmación de Archivo",
                      content=content,
                      size_hint=(0.8, 0.4))
        
        boton_aceptar.bind(on_press=popup.dismiss)
        popup.open()

if __name__ == '__main__':
    InterfazApp().run()