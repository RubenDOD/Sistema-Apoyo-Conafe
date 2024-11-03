from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from collections import OrderedDict
from utils.datatable import DataTable
from datetime import datetime
import hashlib
import mysql.connector
from kivy.uix.boxlayout import BoxLayout
import webbrowser
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder

class AdminWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Builder.load_file("admin.kv")  # Carga explícita de admin.kv
        self.mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='pos'
        )
        self.mycursor = self.mydb.cursor()

        content = self.ids.scrn_contents
        users = self.get_users()
        userstable = DataTable(table=users, callback=self.button_callback)  # Pasa button_callback aquí
        content.add_widget(userstable)

        #Display Products
        #product_scrn = self.ids.scrn_product_content
        #products = self.get_products()
        #prod_table = DataTable(table=products)
        #product_scrn.add_widget(prod_table)


    def button_callback(self, button_text, idx):
        if button_text == 'Aceptar':
            self.aceptar_user(idx)
        elif button_text == 'Rechazar':
            self.rechazar_user(idx)
        elif button_text == 'Ver':
            self.ver_user(idx)

    def aceptar_user(self, idx):
        print(f"Aqui en teoria acepto a {idx}")
        

    def rechazar_user(self, idx):
        print(f"Aqui en teoria elimino a {idx}")
        # Implementa la lógica para eliminar un usuario aquí



    def ver_user(self, idx):
        content = self.ids.scrn_view
        # Obtén los datos del usuario en base al índice
        users = self.get_users()
        user_info = {key: users[key][idx] for key in users}

        # Limpia la pantalla de visualización de usuario
        content.clear_widgets()

        # Crea un ScrollView para que el contenido sea desplazable
        scroll_view = ScrollView(size_hint=(1, 1))

        # Crea un layout para mostrar los datos del usuario
        user_info_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        user_info_layout.bind(minimum_height=user_info_layout.setter('height'))

        # Agrega botones con información del usuario
        for key, value in user_info.items():
            user_info_layout.add_widget(Button(text=f"{key}: {value}", size_hint_y=None, height=50))

        # Botón para ver documentos
        documentos_button = Button(text="Ver documentos", size_hint_y=None, height=50)
        documentos_button.bind(on_release=self.ver_documentos)

        # Botón para volver a la pantalla principal
        back_button = Button(text="Regresar", size_hint_y=None, height=50)
        back_button.bind(on_release=self.go_back)

        # Agrega los botones al layout
        user_info_layout.add_widget(documentos_button)
        user_info_layout.add_widget(back_button)

        # Agrega el layout al ScrollView
        scroll_view.add_widget(user_info_layout)

        # Agrega el ScrollView al contenido
        content.add_widget(scroll_view)

        # Cambia a la pantalla de visualización de usuario
        self.ids.scrn_mngr.current = 'scrn_view'

    def ver_documentos(self, instance):
        # Lógica para mostrar documentos del usuario
        webbrowser.open('https://www.google.com')
        print("Ver documentos presionado")

    def go_back(self, instance):
        self.ids.scrn_mngr.current = 'scrn_content'


        

    def add_user_fields(self):
        target = self.ids.ops_fields
        target.clear_widgets()
        crud_first = TextInput(hint_text='First Name')
        crud_last = TextInput(hint_text='Last Name')
        crud_user = TextInput(hint_text='User Name')
        crud_pwd = TextInput(hint_text='Password')
        crud_des = Spinner(text='Operator',values=['Operator','Administrator'])
        crud_submit = Button(text='Add',size_hint_x=None,width=100,on_release=lambda x: self.add_user(crud_first.text,crud_last.text,crud_user.text,crud_pwd.text,crud_des.text))

        target.add_widget(crud_first)
        target.add_widget(crud_last)
        target.add_widget(crud_user)
        target.add_widget(crud_pwd)
        target.add_widget(crud_des)
        target.add_widget(crud_submit)
    
    def add_user(self, first,last,user,pwd,des):
        content = self.ids.scrn_contents
        content.clear_widgets()
        sql = 'INSERT INTO users(first_name,last_name,user_name,password,designation,date) VALUES(%s,%s,%s,%s,%s,%s)'
        values =[first,last,user,pwd,des,datetime.now()]

        self.mycursor.execute(sql,values)
        self.mydb.commit()

        users = self.get_users()
        userstable = DataTable(table=users)
        content.add_widget(userstable)
    
    def update_user_fields(self):
        target = self.ids.ops_fields
        target.clear_widgets()
        crud_first = TextInput(hint_text='First Name')
        crud_last = TextInput(hint_text='Last Name')
        crud_user = TextInput(hint_text='User Name')
        crud_pwd = TextInput(hint_text='Password')
        crud_des = Spinner(text='Operator',values=['Operator','Administrator'])
        crud_submit = Button(text='Update',size_hint_x=None,width=100,on_release=lambda x: self.update_user(crud_first.text,crud_last.text,crud_user.text,crud_pwd.text,crud_des.text))

        target.add_widget(crud_first)
        target.add_widget(crud_last)
        target.add_widget(crud_user)
        target.add_widget(crud_pwd)
        target.add_widget(crud_des)
        target.add_widget(crud_submit)
    
    def update_user(self, first,last,user,pwd,des):
        content = self.ids.scrn_contents
        content.clear_widgets()
        pwd = hashlib.sha256(pwd.encode()).hexdigest()
        
        sql = 'UPDATE users SET first_name=%s,last_name=%s,user_name=%s,password=%s,designation=%s WHERE user_name=%s'
        print(pwd)
        values =[first,last,user,pwd,des,user]

        self.mycursor.execute(sql,values)
        self.mydb.commit()

        users = self.get_users()
        userstable = DataTable(table=users)
        content.add_widget(userstable)

    def get_users(self):
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='pos'
        )
        mycursor = mydb.cursor()
        _users = OrderedDict()
        _users['first_names'] = {}
        _users['last_names'] = {}
        _users['user_names'] = {}
        first_names = []
        last_names = []
        user_names = []

        sql = 'SELECT * FROM users'
        mycursor.execute(sql)
        users = mycursor.fetchall()
        for user in users:
            first_names.append(user[1])
            last_names.append(user[2])
            user_names.append(user[3])
        # print(designations)
        users_length = len(first_names)
        idx = 0
        while idx < users_length:
            _users['first_names'][idx] = first_names[idx]
            _users['last_names'][idx] = last_names[idx]
            _users['user_names'][idx] = user_names[idx]

            idx += 1
        
        return _users
    
    def get_products(self):
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='pos'
        )
        mycursor = mydb.cursor()
        _stocks = OrderedDict()
        _stocks['product_code'] = {}
        _stocks['product_name'] = {}
        _stocks['product_weight'] = {}
        _stocks['in_stock'] = {}
        _stocks['sold'] = {}
        _stocks['order'] = {}
        _stocks['last_purchase'] = {}

        product_code = []
        product_name = []
        product_weight = []
        in_stock = []
        sold = []
        order = []
        last_purchase = []
        sql = 'SELECT * FROM stocks'
        mycursor.execute(sql)
        products = mycursor.fetchall()
        for product in products:
            product_code.append(product[1])
            name = product[2]
            if len(name) > 10:
                name = name[:10] + '...'
            product_name.append(name)
            product_weight.append(product[3])
            in_stock.append(product[5])
            sold.append(product[6])
            order.append(product[7])
            last_purchase.append(product[8])
        # print(designations)
        products_length = len(product_code)
        idx = 0
        while idx < products_length:
            _stocks['product_code'][idx] = product_code[idx]
            _stocks['product_name'][idx] = product_name[idx]
            _stocks['product_weight'][idx] = product_weight[idx]
            _stocks['in_stock'][idx] = in_stock[idx]
            _stocks['sold'][idx] = sold[idx]
            _stocks['order'][idx] = order[idx]
            _stocks['last_purchase'][idx] = last_purchase[idx]
           

            idx += 1
        
        return _stocks
        
    def change_screen(self, instance):
        if instance.text == 'Manage Products':
            self.ids.scrn_mngr.current = 'scrn_product_content'
        elif instance.text == 'Manage Users':
            self.ids.scrn_mngr.current = 'scrn_content'
        else:
            self.ids.scrn_mngr.current = 'scrn_view' 


class AdminApp(App):
    def build(self):

        return AdminWindow()

if __name__=='__main__':
    AdminApp().run()