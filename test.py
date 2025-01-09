import pyodbc

# Listar los controladores ODBC disponibles
available_drivers = pyodbc.drivers()
print("Controladores ODBC disponibles:", available_drivers)