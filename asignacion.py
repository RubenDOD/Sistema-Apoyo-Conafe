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
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner  

class AdminWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Builder.load_file("admin.kv")  # Carga explícita de admin.kv
        self.mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='CONAFE'
        )
        self.mycursor = self.mydb.cursor()

        content = self.ids.scrn_contents
        users = self.get_users("General", 0)
        userstable = DataTable(table=users, callback=self.button_callback)  # Pasa button_callback aquí
        content.add_widget(userstable)

        #Display Products
        #product_scrn = self.ids.scrn_product_content
        #products = self.get_products()
        #prod_table = DataTable(table=products)
        #product_scrn.add_widget(prod_table)

    def reload_users(self):
        # Obtiene el contenedor de usuarios
        content = self.ids.scrn_contents
        content.clear_widgets()

        # Obtiene nuevamente la lista de usuarios
        users = self.get_users("General", 0)

        # Crea la tabla actualizada y agrégala a la pantalla
        userstable = DataTable(table=users, callback=self.button_callback)
        content.add_widget(userstable)

    def button_callback(self, button_text, idx):
        if button_text == 'Ver':
            self.ver_user(idx)


    def ver_user(self, idx):
        content = self.ids.scrn_view
        users = self.get_users("User", idx)
        user_info = {key: users[key][idx] for key in users}

        content.clear_widgets()
        scroll_view = ScrollView(size_hint=(1, 1))
        user_info_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        user_info_layout.bind(minimum_height=user_info_layout.setter('height'))

        values = list(user_info.values())
        
        aspirante_text = f"Aspirante: {values[1]} {values[2]} {values[3]}"
        user_info_layout.add_widget(Label(text=aspirante_text, color=(0, 0, 0, 1), size_hint_y=None, height=50, halign='left', valign='middle'))

        aspirante_text2 = f"Fecha de nacimiento: {values[4]}"
        user_info_layout.add_widget(Label(text=aspirante_text2, color=(0, 0, 0, 1), size_hint_y=None, height=50, halign='left', valign='middle'))
        
        residencia_text = f"Residencia: {values[6]}, {values[7]}, {values[5]}"
        user_info_layout.add_widget(Label(text=residencia_text, color=(0, 0, 0, 1), size_hint_y=None, height=50, halign='left', valign='middle'))
        
        estado_text = f"Estado preferente: {values[8]}"
        user_info_layout.add_widget(Label(text=estado_text, color=(0, 0, 0, 1), size_hint_y=None, height=50, halign='left', valign='middle'))

        estado_text2 = f"en el municipio: {values[10]}"
        user_info_layout.add_widget(Label(text=estado_text2, color=(0, 0, 0, 1), size_hint_y=None, height=50, halign='left', valign='middle'))

        ciclo_text = f"Ciclo: {values[9]}"
        user_info_layout.add_widget(Label(text=ciclo_text, color=(0, 0, 0, 1), size_hint_y=None, height=50, halign='left', valign='middle'))

        estado = values[8].replace("CONAFE ", "")

        # Primer Spinner: Selección del CCT
        dropdown_values = self.get_dropdown_options(estado)
        spinner_cct = Spinner(
            text="Selecciona un CCT",
            values=dropdown_values,
            size_hint=(1, None),
            height=50
        )

        # Segundo Spinner: Capacitadores del CCT seleccionado
        spinner_capacitador = Spinner(
            text="Capacitador",
            values=[],  # Vacío inicialmente
            size_hint=(1, None),
            height=50
        )

        # Método para actualizar el segundo Spinner cuando cambie el primer Spinner
        def on_cct_select(spinner, text):
            claveCentro = text.split(' - ')[0]  # Obtiene solo el claveCentro del texto seleccionado
            capacitadores = self.get_capacitadores_by_cct(claveCentro)
            spinner_capacitador.values = capacitadores

        spinner_cct.bind(text=on_cct_select)

        # Añadir ambos Spinner al layout
        user_info_layout.add_widget(spinner_cct)
        user_info_layout.add_widget(spinner_capacitador)

        # Botón para volver a la pantalla principal
        back_button = Button(text="Regresar", size_hint_y=None, height=50)
        back_button.bind(on_release=self.go_back)

        user_info_layout.add_widget(back_button)
        scroll_view.add_widget(user_info_layout)
        content.add_widget(scroll_view)
        self.ids.scrn_mngr.current = 'scrn_view'

    def get_dropdown_options(self, estado):
        # Conecta a la base de datos y obtiene las opciones
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='CONAFE'
        )
        mycursor = mydb.cursor()
        
        # Ejecuta el query para obtener claveCentro, nombre y municipio
        sql = 'SELECT claveCentro, nombre, municipio FROM CCT WHERE CCT.estado = %s'
        mycursor.execute(sql, (estado,))
        result = mycursor.fetchall()
        
        # Formatea los resultados para mostrarlos en el dropdown
        options = [f"{claveCentro} - {nombre}, {municipio}" for claveCentro, nombre, municipio in result]
        
        mycursor.close()
        mydb.close()
        
        return options

    def get_capacitadores_by_cct(self, claveCentro):
        # Conecta a la base de datos y obtiene los capacitadores para el CCT seleccionado
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='CONAFE'
        )
        mycursor = mydb.cursor()

        # Primero, obtenemos el id_LEC correspondiente al claveCentro seleccionado
        sql = '''
            SELECT LEC.id_Usuario 
            FROM CentroEducador
            JOIN LEC ON CentroEducador.id_LEC = LEC.id_Usuario
            WHERE CentroEducador.claveCentro = %s
        '''
        mycursor.execute(sql, (claveCentro,))
        lec_ids = [row[0] for row in mycursor.fetchall()]

        # Ahora obtenemos los nombres y apellidos de los usuarios con acceso "Capacitador" y en los lec_ids obtenidos
        sql = '''
            SELECT Aspirante.nombres, Aspirante.apellidoPaterno, Aspirante.apellidoMaterno 
            FROM Usuario
            JOIN Aspirante ON Usuario.id_Usuario = Aspirante.id_Aspirante
            WHERE Usuario.acceso = 'Capacitador' AND Usuario.id_Usuario IN (%s)
        ''' % ','.join(['%s'] * len(lec_ids))  # Genera el número adecuado de placeholders
        mycursor.execute(sql, tuple(lec_ids))
        result = mycursor.fetchall()

        # Formatea los resultados para mostrarlos en el dropdown
        capacitadores = [f"{nombres} {apellidoPaterno} {apellidoMaterno}" for nombres, apellidoPaterno, apellidoMaterno in result]

        mycursor.close()
        mydb.close()
        
        return capacitadores



    def ver_documento(self, url):
        # Lógica para abrir el documento específico
        if url:  # Asegúrate de que el URL no esté vacío
            webbrowser.open(url)
        else:
            print("URL no disponible para este documento")

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

        users = self.get_users("General", 0)
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

        users = self.get_users("General", 0)
        userstable = DataTable(table=users)
        content.add_widget(userstable)

    def get_users(self, mode, id):
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='CONAFE'
        )
        mycursor = mydb.cursor()

        if mode == "General":
            _users = OrderedDict()
            _users['ID'] = {}
            _users['first_names'] = {}
            _users['last_names'] = {}
            _users['user_names'] = {}
            ids = []
            first_names = []
            last_names = []
            user_names = []

            sql = 'SELECT * FROM Aspirante WHERE estado_solicitud = %s'
            mycursor.execute(sql, ("Pendiente",))

            users = mycursor.fetchall()
            for user in users:
                ids.append(user[0])
                first_names.append(user[6])
                last_names.append(user[7])
                user_names.append(user[8])
            # print(designations)
            users_length = len(first_names)
            idx = 0
            while idx < users_length:
                _users['ID'][idx] = ids[idx]
                _users['first_names'][idx] = first_names[idx]
                _users['last_names'][idx] = last_names[idx]
                _users['user_names'][idx] = user_names[idx]

                idx += 1
            
            return _users
        else:
            # Lista de claves
            keys = [
                'ID', 'nombres', 'apellidoPat', 'apellidoMat', 'Fecha Nacimiento',
                'Codigo Postal', 'Estado', 'Municipio',
                'Estado Preferente', 'Ciclo', 'Municipio Deseado'
            ]

            # Crear OrderedDict usando una comprensión

            _users = OrderedDict((key, {}) for key in keys)

            sql = 'SELECT * FROM Aspirante WHERE estado_solicitud = %s'
            mycursor.execute(sql, ("Pendiente",))

            users = mycursor.fetchall()
            id_final = users[id][0]
            sql = 'SELECT * FROM Aspirante WHERE id_Aspirante = %s'
            mycursor.execute(sql, (id_final,))

            users = mycursor.fetchall()
            idx = 0

            for user in users:
                _users['ID'][idx] = user[0]
                _users['nombres'][idx] = user[6]
                _users['apellidoPat'][idx] = user[7]
                _users['apellidoMat'][idx] = user[8]
                _users['Fecha Nacimiento'][idx] = user[9]

            sql = 'SELECT * FROM ResidenciaAspirante WHERE id_Aspirante = %s'
            mycursor.execute(sql, (id_final,))

            users = mycursor.fetchall()

            for user in users:
                _users['Codigo Postal'][idx] = user[1]
                _users['Estado'][idx] = user[2]
                _users['Municipio'][idx] = user[3]
            
            sql = 'SELECT * FROM ParticipacionAspirante WHERE id_Aspirante = %s'
            mycursor.execute(sql, (id_final,))

            users = mycursor.fetchall()

            for user in users:
                _users['Estado Preferente'][idx] = user[1]
                _users['Ciclo'][idx] = user[2]
                _users['Municipio Deseado'][idx] = user[4]

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