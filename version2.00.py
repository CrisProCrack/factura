import tkinter as tk
from tkinter import messagebox, ttk
import re
import datetime
import os
import mysql.connector
from mysql.connector import Error
import reportlab
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Database configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "facturacion",
    "port": "3306"  # Default MySQL port
}

def conectar_bd():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"Connected to MySQL Server version {db_info}")
            return connection
    except Error as e:
        messagebox.showerror("Error de Conexión", f"Error: {e}")
        return None

def test_connection():
    conn = conectar_bd()
    if conn:
        messagebox.showinfo("Éxito", "Conexión exitosa a la base de datos")
        conn.close()
    else:
        messagebox.showerror("Error", "No se pudo conectar a la base de datos")


# Definición de colores
COLOR_FONDO = "#ffe6f0"
COLOR_BOTON = "#ff66b2"
COLOR_TEXTO_BOTON = "#ffffff"
COLOR_CAMPO = "#fff0f5"


# Ventana principal de la aplicación
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Factgre")
        self.root.geometry("400x350")
        self.root.configure(bg=COLOR_FONDO)

        title = tk.Label(self.root, text="Bienvenido a Factgre", font=("Arial", 18, "bold"),
                         bg=COLOR_FONDO, fg=COLOR_BOTON)
        title.pack(pady=20)

        btn_login = tk.Button(self.root, text="Iniciar Sesión", width=20, height=2,
                              bg=COLOR_BOTON, fg=COLOR_TEXTO_BOTON, command=self.iniciar_sesion)
        btn_login.pack(pady=10)

        btn_register = tk.Button(self.root, text="Registrar Usuario", width=20, height=2,
                                 bg=COLOR_BOTON, fg=COLOR_TEXTO_BOTON, command=self.registrar_usuario)
        btn_register.pack(pady=10)

        btn_recover = tk.Button(self.root, text="Recuperar Contraseña", width=20, height=2,
                                bg=COLOR_BOTON, fg=COLOR_TEXTO_BOTON, command=self.recuperar_contrasena)
        btn_recover.pack(pady=10)

    def iniciar_sesion(self):
        LoginWindow(self.root)

    def registrar_usuario(self):
        RegisterWindow(self.root)

    def recuperar_contrasena(self):
        # Aquí puedes implementar la función de recuperación de contraseña si lo deseas
        pass

# Ventana de Registro de Usuario
class RegisterWindow:
    def __init__(self, root):
        self.root = tk.Toplevel(root)
        self.root.title("Registro de Usuario")
        self.root.geometry("300x450")
        self.root.configure(bg=COLOR_FONDO)

        title = tk.Label(self.root, text="Registro de Usuario", 
                        font=("Arial", 16, "bold"),
                        bg=COLOR_FONDO, fg=COLOR_BOTON)
        title.pack(pady=10)

        # Create entry fields with consistent names
        self.entry_usuario = self.crear_campo("Usuario")
        self.entry_contrasena = self.crear_campo("Contraseña", show="*")
        self.entry_confirmar_contrasena = self.crear_campo("Confirmar Contraseña", show="*")
        self.entry_correo = self.crear_campo("Correo")
        self.entry_telefono = self.crear_campo("Teléfono")

        btn_registrar = tk.Button(
            self.root,
            text="Registrar",
            command=self.registrar,
            bg=COLOR_BOTON,
            fg=COLOR_TEXTO_BOTON
        )
        btn_registrar.pack(pady=20)

    def crear_campo(self, texto, show=None):
        label = tk.Label(self.root, text=texto, bg=COLOR_FONDO, fg=COLOR_BOTON)
        label.pack(pady=5)
        entry = tk.Entry(self.root, show=show, bg=COLOR_CAMPO, fg="black")
        entry.pack(pady=5)
        return entry

    def registrar(self):
        usuario = self.entry_usuario.get().strip()
        contrasena = self.entry_contrasena.get().strip()
        confirmar = self.entry_confirmar_contrasena.get().strip()
        correo = self.entry_correo.get().strip()
        telefono = self.entry_telefono.get().strip()

        # Validate fields
        if not all([usuario, contrasena, confirmar, correo]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        if contrasena != confirmar:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return

        try:
            conn = conectar_bd()
            if conn:
                cursor = conn.cursor()
                # Check if user exists
                cursor.execute("SELECT id FROM usuarios WHERE usuario = %s OR correo = %s", 
                             (usuario, correo))
                if cursor.fetchone():
                    messagebox.showerror("Error", "Usuario o correo ya existe")
                    return

                # Insert new user
                cursor.execute("""
                    INSERT INTO usuarios (usuario, contrasena, correo, telefono)
                    VALUES (%s, %s, %s, %s)
                """, (usuario, contrasena, correo, telefono))
                
                conn.commit()
                messagebox.showinfo("Éxito", "Usuario registrado correctamente")
                self.root.destroy()
                
        except Error as e:
            messagebox.showerror("Error", f"Error en la base de datos: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

# Ventana de Inicio de Sesión
class LoginWindow:
    def __init__(self, root):
        self.root = tk.Toplevel(root)
        self.root.title("Inicio de Sesión")
        self.root.geometry("300x300")
        self.root.configure(bg=COLOR_FONDO)

        title = tk.Label(self.root, text="Inicio de Sesión", 
                        font=("Arial", 16, "bold"),
                        bg=COLOR_FONDO, fg=COLOR_BOTON)
        title.pack(pady=10)

        self.entry_usuario = self.crear_campo("Usuario")
        self.entry_contrasena = self.crear_campo("Contraseña", show="*")

        btn_login = tk.Button(
            self.root,
            text="Iniciar Sesión",
            command=self.login,
            bg=COLOR_BOTON,
            fg=COLOR_TEXTO_BOTON
        )
        btn_login.pack(pady=20)

    def crear_campo(self, texto, show=None):
        label = tk.Label(self.root, text=texto, bg=COLOR_FONDO, fg=COLOR_BOTON)
        label.pack(pady=5)
        entry = tk.Entry(self.root, show=show, bg=COLOR_CAMPO, fg="black")
        entry.pack(pady=5)
        return entry

    def login(self):
        usuario = self.entry_usuario.get().strip()
        contrasena = self.entry_contrasena.get().strip()

        if not usuario or not contrasena:
            messagebox.showerror("Error", "Por favor complete todos los campos")
            return

        try:
            conn = conectar_bd()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, usuario 
                    FROM usuarios 
                    WHERE usuario = %s AND contrasena = %s
                """, (usuario, contrasena))
                
                usuario_data = cursor.fetchone()
                
                if usuario_data:
                    messagebox.showinfo("Éxito", "Inicio de sesión exitoso")
                    self.root.destroy()
                    MainScreen(self.root.master, usuario_data[0])
                else:
                    messagebox.showerror("Error", "Usuario o contraseña incorrectos")

        except Error as e:
            messagebox.showerror("Error", f"Error en la base de datos: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

# Pantalla Principal
class MainScreen:
    def __init__(self, root,user_id):
        self.root = tk.Toplevel(root)
        self.root.title("Sistema de Facturación")
        self.root.geometry("800x600")
        self.root.configure(bg=COLOR_FONDO)
        self.user_id = user_id

        title = tk.Label(self.root, text="Factgre", font=("Arial", 18, "bold"),
                         bg=COLOR_FONDO, fg=COLOR_BOTON)
        title.pack(pady=20)

        btn_productos = tk.Button(self.root, text="Gestión de Productos", width=25, height=2,
                                  bg=COLOR_BOTON, fg=COLOR_TEXTO_BOTON, command=self.gestion_productos)
        btn_productos.pack(pady=10)

        btn_clientes = tk.Button(self.root, text="Gestión de Clientes", width=25, height=2,
                                 bg=COLOR_BOTON, fg=COLOR_TEXTO_BOTON, command=self.gestion_clientes)
        btn_clientes.pack(pady=10)

        btn_facturacion = tk.Button(self.root, text="Facturación", width=25, height=2,
                                    bg=COLOR_BOTON, fg=COLOR_TEXTO_BOTON, command=self.facturacion)
        btn_facturacion.pack(pady=10)

        btn_visualizar_facturas = tk.Button(self.root, text="Visualizar Facturas", width=25, height=2,
                                            bg=COLOR_BOTON, fg=COLOR_TEXTO_BOTON, command=self.visualizar_facturas)
        btn_visualizar_facturas.pack(pady=10)

    def gestion_productos(self):
        ProductosCRUD(self.root)

    def gestion_clientes(self):
        ClientesCRUD(self.root)

    def facturacion(self):
        FacturacionWindow(self.root)

    def visualizar_facturas(self):
        FacturasListWindow(self.root)

# CRUD de Productos
class ProductosCRUD:
    def __init__(self, root):
        self.root = tk.Toplevel(root)
        self.root.title("Gestión de Productos")
        self.root.geometry("800x600")
        self.root.configure(bg=COLOR_FONDO)
        
        # Initialize productos dictionary
        self.productos = {}

        self.create_ui()
        self.cargar_productos()

    def create_ui(self):
        # Title and Add button frame
        top_frame = tk.Frame(self.root, bg=COLOR_FONDO)
        top_frame.pack(pady=10, fill=tk.X)

        title = tk.Label(top_frame, text="Gestión de Productos", 
                        font=("Arial", 16, "bold"),
                        bg=COLOR_FONDO, fg=COLOR_BOTON)
        title.pack(side=tk.LEFT, padx=20)

        btn_add = tk.Button(top_frame, text="+ Agregar Producto",
                           command=self.agregar_producto,
                           bg=COLOR_BOTON, fg=COLOR_TEXTO_BOTON)
        btn_add.pack(side=tk.RIGHT, padx=20)

        # Create table
        columns = ("ID", "Código", "Nombre", "Descripción", "Precio", "Cantidad")
        self.tabla = ttk.Treeview(self.root, columns=columns, show="headings")
        
        # Configure columns
        for col in columns:
            self.tabla.heading(col, text=col)
            width = 100 if col not in ["Descripción", "Nombre"] else 200
            self.tabla.column(col, width=width)
        
        self.tabla.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

    def cargar_productos(self):
        # Clear existing items
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        try:
            conn = conectar_bd()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, codigo, nombre, descripcion, precio, cantidad 
                    FROM productos
                """)
                productos_data = cursor.fetchall()
                
                # Clear existing dictionary
                self.productos.clear()
                
                # Load products into table and dictionary
                for producto in productos_data:
                    self.tabla.insert("", "end", values=producto)
                    
                    # Store in dictionary using id as key
                    self.productos[producto[0]] = {
                        'id': producto[0],
                        'codigo': producto[1],
                        'nombre': producto[2],
                        'descripcion': producto[3],
                        'precio': producto[4],
                        'cantidad': producto[5]
                    }
                
        except Error as e:
            messagebox.showerror("Error", f"Error al cargar productos: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def create_widgets(self):
        # Table frame
        frame_tabla = tk.Frame(self.root, bg=COLOR_FONDO)
        frame_tabla.pack(pady=10, padx=10, fill="both", expand=True)

        # Create Treeview
        self.tabla = ttk.Treeview(frame_tabla, columns=("Código", "Nombre", "Descripción", "Precio", "Cantidad"))
        self.tabla.heading("#0", text="ID")
        self.tabla.heading("Código", text="Código")
        self.tabla.heading("Nombre", text="Nombre")
        self.tabla.heading("Descripción", text="Descripción")
        self.tabla.heading("Precio", text="Precio")
        self.tabla.heading("Cantidad", text="Cantidad")
        self.tabla.pack(fill="both", expand=True)

    def cargar_productos(self):
        try:
            conn = conectar_bd()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, codigo, nombre, descripcion, precio, cantidad FROM productos")
                productos_data = cursor.fetchall()
                
                # Clear existing items
                for item in self.tabla.get_children():
                    self.tabla.delete(item)
                
                # Load products into table
                for producto in productos_data:
                    self.tabla.insert("", "end", text=str(producto[0]),
                                    values=(producto[1], producto[2], 
                                           producto[3], producto[4], 
                                           producto[5]))
                    # Store in dictionary
                    self.productos[producto[1]] = {
                        'id': producto[0],
                        'nombre': producto[2],
                        'descripcion': producto[3],
                        'precio': producto[4],
                        'cantidad': producto[5]
                    }
                
        except Error as e:
            messagebox.showerror("Error", f"Error al cargar productos: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def agregar_producto(self):
        codigo = self.entry_codigo.get().strip()
        nombre = self.entry_nombre.get().strip()
        descripcion = self.entry_descripcion.get().strip()
        precio = self.entry_precio.get().strip()
        cantidad = self.entry_cantidad.get().strip()

        # Validate fields
        if not all([codigo, nombre, descripcion, precio, cantidad]):
            messagebox.showerror("Error", "Por favor complete todos los campos.")
            return

        try:
            precio = float(precio)
            cantidad = int(cantidad)
        except ValueError:
            messagebox.showerror("Error", "Precio debe ser un número y cantidad un entero.")
            return

        try:
            conn = conectar_bd()
            if conn:
                cursor = conn.cursor()
                # Check if code exists
                cursor.execute("SELECT id FROM productos WHERE codigo = %s", (codigo,))
                if cursor.fetchone():
                    messagebox.showerror("Error", "El código de producto ya existe.")
                    return

                # Insert new product
                cursor.execute("""
                    INSERT INTO productos (codigo, nombre, descripcion, precio, cantidad)
                    VALUES (%s, %s, %s, %s, %s)
                """, (codigo, nombre, descripcion, precio, cantidad))
                conn.commit()

                self.tabla.insert("", "end", values=(codigo, nombre, descripcion, 
                                                   f"${precio:.2f}", cantidad))
                messagebox.showinfo("Éxito", "Producto agregado correctamente.")
                self.limpiar_campos()

        except Error as e:
            messagebox.showerror("Error", f"Error al agregar producto: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def modificar_producto(self):
        selected_items = self.tabla.selection()
        if not selected_items:
            messagebox.showerror("Error", "Seleccione un producto para modificar.")
            return

        selected_item = selected_items[0]
        valores = self.tabla.item(selected_item, "values")
        codigo_original = valores[0]

        try:
            conn = conectar_bd()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM productos WHERE codigo = %s
                """, (codigo_original,))
                producto = cursor.fetchone()
                if producto:
                    ProductoForm(self.root, self.tabla, codigo_original, 
                               self.actualizar_productos)
                else:
                    messagebox.showerror("Error", "Producto no encontrado.")

        except Error as e:
            messagebox.showerror("Error", f"Error al modificar producto: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def eliminar_producto(self):
        selected_items = self.tabla.selection()
        if not selected_items:
            messagebox.showerror("Error", "Seleccione un producto para eliminar.")
            return

        selected_item = selected_items[0]
        valores = self.tabla.item(selected_item, "values")
        codigo = valores[0]

        if messagebox.askyesno("Confirmar", 
                             f"¿Está seguro de eliminar el producto con código '{codigo}'?"):
            try:
                conn = conectar_bd()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM productos WHERE codigo = %s", (codigo,))
                    conn.commit()
                    
                    self.tabla.delete(selected_item)
                    messagebox.showinfo("Éxito", "Producto eliminado correctamente.")

            except Error as e:
                messagebox.showerror("Error", f"Error al eliminar producto: {e}")
            finally:
                if 'conn' in locals() and conn.is_connected():
                    cursor.close()
                    conn.close()

    def limpiar_campos(self):
        for entry in [self.entry_codigo, self.entry_nombre, 
                     self.entry_descripcion, self.entry_precio, 
                     self.entry_cantidad]:
            entry.delete(0, tk.END)

# Formulario para Modificar Producto
class ProductoForm:
    def __init__(self, root, tree, codigo_original, callback):
        self.root = tk.Toplevel(root)
        self.root.title("Modificar Producto")
        self.root.geometry("300x400")
        self.root.configure(bg=COLOR_FONDO)
        self.tree = tree
        self.codigo_original = codigo_original
        self.callback = callback

        # Título
        title_text = "Modificar Producto"
        title = tk.Label(self.root, text=title_text, font=("Arial", 16, "bold"),
                         bg=COLOR_FONDO, fg=COLOR_BOTON)
        title.pack(pady=10)

        # Campos de entrada
        self.entry_codigo = self.crear_campo("Código")
        self.entry_nombre = self.crear_campo("Nombre")
        self.entry_descripcion = self.crear_campo("Descripción")
        self.entry_precio = self.crear_campo("Precio")
        self.entry_cantidad = self.crear_campo("Cantidad")

        # Cargar datos actuales
        self.cargar_datos()

        # Botón de guardar cambios
        btn_save = tk.Button(self.root, text="Guardar Cambios", width=15, height=2,
                             bg=COLOR_BOTON, fg=COLOR_TEXTO_BOTON, command=self.guardar_cambios)
        btn_save.pack(pady=20)

    def crear_campo(self, texto):
        label = tk.Label(self.root, text=texto, bg=COLOR_FONDO, fg=COLOR_BOTON)
        label.pack(pady=5)
        entry = tk.Entry(self.root, bg=COLOR_CAMPO, fg="black")
        entry.pack(pady=5)
        return entry

    def cargar_datos(self):
        try:
            conn = conectar_bd()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT codigo, nombre, descripcion, precio, cantidad 
                    FROM productos WHERE codigo = %s
                """, (self.codigo_original,))
                producto = cursor.fetchone()
                
                if producto:
                    self.entry_codigo.insert(0, producto[0])
                    self.entry_nombre.insert(0, producto[1])
                    self.entry_descripcion.insert(0, producto[2])
                    self.entry_precio.insert(0, f"{float(producto[3]):.2f}")
                    self.entry_cantidad.insert(0, str(producto[4]))
        except Error as e:
            messagebox.showerror("Error", f"Error al cargar producto: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def guardar_cambios(self):
        codigo = self.entry_codigo.get().strip()
        nombre = self.entry_nombre.get().strip()
        descripcion = self.entry_descripcion.get().strip()
        precio = self.entry_precio.get().strip()
        cantidad = self.entry_cantidad.get().strip()

        if not all([codigo, nombre, descripcion, precio, cantidad]):
            messagebox.showerror("Error", "Por favor, complete todos los campos.")
            return

        try:
            precio = float(precio)
            cantidad = int(cantidad)
        except ValueError:
            messagebox.showerror("Error", "Precio debe ser un número y cantidad un entero.")
            return

        try:
            conn = conectar_bd()
            if conn:
                cursor = conn.cursor()
                
                # Check if new code exists (if code was changed)
                if codigo != self.codigo_original:
                    cursor.execute("SELECT id FROM productos WHERE codigo = %s", (codigo,))
                    if cursor.fetchone():
                        messagebox.showerror("Error", "El nuevo código ya existe.")
                        return

                # Update product
                cursor.execute("""
                    UPDATE productos 
                    SET codigo = %s, nombre = %s, descripcion = %s, 
                        precio = %s, cantidad = %s
                    WHERE codigo = %s
                """, (codigo, nombre, descripcion, precio, cantidad, self.codigo_original))
                
                conn.commit()
                self.callback()  # Refresh table
                messagebox.showinfo("Éxito", "Producto modificado correctamente.")
                self.root.destroy()

        except Error as e:
            messagebox.showerror("Error", f"Error al modificar producto: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

# CRUD de Clientes
class ClientesCRUD:
    def __init__(self, root):
        self.root = tk.Toplevel(root)
        self.root.title("Gestión de Clientes")
        self.root.geometry("500x400")
        self.root.configure(bg=COLOR_FONDO)

        # Title and Add button in same frame
        top_frame = tk.Frame(self.root, bg=COLOR_FONDO)
        top_frame.pack(pady=10, fill=tk.X)

        title = tk.Label(top_frame, text="Gestión de Clientes", 
                        font=("Arial", 16, "bold"),
                        bg=COLOR_FONDO, fg=COLOR_BOTON)
        title.pack(side=tk.LEFT, padx=20)

        btn_add = tk.Button(top_frame, text="+ Agregar Cliente",
                           command=self.agregar_cliente,
                           bg=COLOR_BOTON, fg=COLOR_TEXTO_BOTON)
        btn_add.pack(side=tk.RIGHT, padx=20)

        # Tabla de clientes
        self.tree = ttk.Treeview(self.root, 
                                columns=("ID", "Nombre", "Correo", "Teléfono", "RFC", "Dirección", "Comuna", "Ciudad"), 
                                show='headings')
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Correo", text="Correo")
        self.tree.heading("Teléfono", text="Teléfono")
        self.tree.heading("RFC", text="RFC")
        self.tree.heading("Dirección", text="Dirección")
        self.tree.heading("Comuna", text="Comuna")
        self.tree.heading("Ciudad", text="Ciudad")
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        # Botones
        btn_frame = tk.Frame(self.root, bg=COLOR_FONDO)
        btn_frame.pack(pady=10)

        for (text, command) in [("Agregar", self.agregar_cliente), 
                              ("Editar", self.editar_cliente),
                              ("Eliminar", self.eliminar_cliente)]:
            tk.Button(btn_frame, text=text, width=10,
                     bg=COLOR_BOTON, fg=COLOR_TEXTO_BOTON,
                     command=command).grid(row=0, column=next(iter(range(3))), padx=5)

        self.cargar_clientes()

    def cargar_clientes(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            conn = conectar_bd()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM clientes")
                clientes = cursor.fetchall()
                
                for cliente in clientes:
                    self.tree.insert("", "end", values=cliente)
                    
        except Error as e:
            messagebox.showerror("Error", f"Error al cargar clientes: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def agregar_cliente(self):
        ClienteForm(self.root, self.cargar_clientes)

    def editar_cliente(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Seleccione un cliente para editar.")
            return
            
        valores = self.tree.item(selected[0])['values']
        ClienteForm(self.root, self.cargar_clientes, valores[0])

    def eliminar_cliente(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Seleccione un cliente para eliminar.")
            return
            
        valores = self.tree.item(selected[0])['values']
        cliente_id = valores[0]
        nombre_cliente = valores[1]
        
        if messagebox.askyesno("Confirmar", 
                              f"¿Está seguro de eliminar al cliente '{nombre_cliente}'?"):
            try:
                conn = conectar_bd()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM clientes WHERE id = %s", (cliente_id,))
                    conn.commit()
                    self.cargar_clientes()
                    messagebox.showinfo("Éxito", 
                                      f"Cliente '{nombre_cliente}' eliminado correctamente.")
                    
            except Error as e:
                messagebox.showerror("Error", f"Error al eliminar cliente: {e}")
            finally:
                if 'conn' in locals() and conn.is_connected():
                    cursor.close()
                    conn.close()

# Formulario para agregar o editar clientes
class ClienteForm:
    def __init__(self, root, callback, cliente_id=None):
        self.root = tk.Toplevel(root)
        self.callback = callback
        self.root.title("Formulario de Cliente")
        self.root.geometry("300x400")
        self.root.configure(bg=COLOR_FONDO)
        self.cliente_id = cliente_id

        # Título
        title_text = "Editar Cliente" if cliente_id else "Agregar Cliente"
        title = tk.Label(self.root, text=title_text, font=("Arial", 16, "bold"),
                         bg=COLOR_FONDO, fg=COLOR_BOTON)
        title.pack(pady=10)

        # Campos de entrada
        self.entry_nombre = self.crear_campo("Nombre")
        self.entry_correo = self.crear_campo("Correo")
        self.entry_telefono = self.crear_campo("Teléfono")
        self.entry_direccion = self.crear_campo("Dirección")  # Nuevo campo
        self.entry_comuna = self.crear_campo("Comuna")        # Nuevo campo
        self.entry_ciudad = self.crear_campo("Ciudad")        # Nuevo campo

        # Si es edición, cargar datos
        if cliente_id:
            self.cargar_datos_cliente()

        btn_save = tk.Button(self.root, text="Guardar",
                           width=15, height=2,
                           bg=COLOR_BOTON, fg=COLOR_TEXTO_BOTON,
                           command=self.guardar_cliente)
        btn_save.pack(pady=20)

    def crear_campo(self, texto):
        label = tk.Label(self.root, text=texto, bg=COLOR_FONDO, fg=COLOR_BOTON)
        label.pack(pady=5)
        entry = tk.Entry(self.root, bg=COLOR_CAMPO, fg="black")
        entry.pack(pady=5)
        return entry
    
    def cargar_datos_cliente(self):
        try:
            conn = conectar_bd()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT nombre, correo, telefono, direccion, comuna, ciudad 
                    FROM clientes WHERE id = %s
                """, (self.cliente_id,))
                cliente = cursor.fetchone()
                
                if cliente:
                    self.entry_nombre.insert(0, cliente[0])
                    self.entry_correo.insert(0, cliente[1])
                    self.entry_telefono.insert(0, cliente[2])
                    self.entry_direccion.insert(0, cliente[3] or '')
                    self.entry_comuna.insert(0, cliente[4] or '')
                    self.entry_ciudad.insert(0, cliente[5] or '')
        except Error as e:
            messagebox.showerror("Error", f"Error al cargar cliente: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def generar_rfc(self, nombre):
        # Función simple para generar un RFC simulado basado en el nombre y una fecha fija
        nombre_parts = nombre.strip().upper().split()
        if len(nombre_parts) < 2:
            nombre_parts.append('X')
        rfc = ''.join([p[0] for p in nombre_parts[:2]])
        fecha = datetime.datetime.now().strftime('%Y%m%d')
        homoclave = 'XXX'
        return rfc + fecha + homoclave

    def guardar_cliente(self):
        global contador_clientes
        nombre = self.entry_nombre.get().strip()
        correo = self.entry_correo.get().strip()
        telefono = self.entry_telefono.get().strip()
        direccion = self.entry_direccion.get().strip()
        comuna = self.entry_comuna.get().strip()
        ciudad = self.entry_ciudad.get().strip()

        # Validaciones
        if not nombre or not correo or not telefono:
            messagebox.showerror("Error", "Por favor, complete todos los campos.")
            return
        if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
            messagebox.showerror("Error", "Ingrese un correo válido.")
            return
        if not telefono.isdigit():
            messagebox.showerror("Error", "El teléfono debe ser numérico.")
            return

        rfc = self.generar_rfc(nombre)

        rfc = self.generar_rfc(nombre)

        try:
            conn = conectar_bd()
            if conn:
                cursor = conn.cursor()
                if not self.cliente_id:
                    # Insert new client
                    cursor.execute("""
                        INSERT INTO clientes 
                        (nombre, correo, telefono, direccion, comuna, ciudad, rfc)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (nombre, correo, telefono, direccion, comuna, ciudad, rfc))
                else:
                    # Update existing client
                    cursor.execute("""
                        UPDATE clientes 
                        SET nombre=%s, correo=%s, telefono=%s, 
                            direccion=%s, comuna=%s, ciudad=%s, rfc=%s
                        WHERE id=%s
                    """, (nombre, correo, telefono, direccion, comuna, ciudad, 
                         rfc, self.cliente_id))
                
                conn.commit()
                messagebox.showinfo("Éxito", 
                                  f"Cliente guardado exitosamente.\nRFC: {rfc}")
                self.callback()
                self.root.destroy()
                
        except Error as e:
            messagebox.showerror("Error", f"Error al guardar cliente: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

# Ventana de Facturación
class FacturacionWindow:
    def __init__(self, root):
        self.root = tk.Toplevel(root)
        self.root.title("Facturación")
        self.root.geometry("900x700")
        self.root.configure(bg="#FFC0CB")  # Fondo en tono rosado

        # Initialize UI elements
        self.init_ui()
        self.actualizar_lista_clientes()

    def init_ui(self):
        # Style configuration
        style = ttk.Style()
        style.configure("TLabel", background=COLOR_FONDO, font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10, "bold"))

        # Top frame with title and new invoice button
        top_frame = tk.Frame(self.root, bg=COLOR_FONDO)
        top_frame.pack(pady=10, fill=tk.X)

        title = tk.Label(top_frame, text="Facturación", 
                        font=("Arial", 16, "bold"),
                        bg=COLOR_FONDO, fg=COLOR_BOTON)
        title.pack(side=tk.LEFT, padx=20)

        btn_add = tk.Button(top_frame, text="+ Nueva Factura",
                           command=self.nueva_factura,
                           bg=COLOR_BOTON, fg=COLOR_TEXTO_BOTON)
        btn_add.pack(side=tk.RIGHT, padx=20)

        # Client selection frame
        frame_top = tk.Frame(self.root, bg=COLOR_FONDO)
        frame_top.pack(padx=10, pady=10, fill=tk.X)

        tk.Label(frame_top, text="Seleccionar Cliente", 
                bg=COLOR_FONDO, font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.cliente_combo = ttk.Combobox(frame_top, font=("Arial", 10), 
                                         width=30, state="readonly")
        self.cliente_combo.grid(row=0, column=1, padx=5, pady=5)
        self.cliente_combo.bind("<<ComboboxSelected>>", self.cargar_datos_cliente)

        # Entry fields
        fields = [
            ("RUT", ""), ("Razón Social", ""),
            ("Giro", ""), ("Teléfono", ""),
            ("Dirección", ""), ("Comuna", ""),
            ("Ciudad", ""), ("Fecha", datetime.datetime.now().strftime("%d/%m/%Y"))
        ]

        self.entries = {}
        for i, (label, default) in enumerate(fields):
            tk.Label(frame_top, text=label, 
                    bg=COLOR_FONDO, font=("Arial", 10)).grid(row=(i+1)//2, 
                    column=((i+1)%2)*2, sticky="w", padx=5, pady=5)
            
            entry = ttk.Entry(frame_top, font=("Arial", 10), width=30)
            entry.insert(0, default)
            entry.grid(row=(i+1)//2, column=((i+1)%2)*2+1, padx=5, pady=5)
            self.entries[label] = entry

        # Products table
        self.create_products_table()

        # Totals section
        self.create_totals_section()

    def create_products_table(self):
        frame_table = tk.Frame(self.root, bg=COLOR_FONDO)
        frame_table.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        columns = ["Código", "Cantidad", "Descripción", "Precio Unit.", "Total"]
        self.table = ttk.Treeview(frame_table, columns=columns, 
                                 show="headings", height=10)
        
        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=100 if col != "Descripción" else 200)
        
        self.table.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def create_totals_section(self):
        frame_totals = tk.Frame(self.root, bg=COLOR_FONDO)
        frame_totals.pack(padx=10, pady=10, fill=tk.X)

        totals = [
            ("Observación", ""), ("Total Neto", "0.00"),
            ("IVA 19%", "0.00"), ("TOTAL", "0.00")
        ]

        self.totals_entries = {}
        for i, (label, default) in enumerate(totals):
            tk.Label(frame_totals, text=label, 
                    bg=COLOR_FONDO, font=("Arial", 10)).grid(row=i, column=0, 
                    sticky="w", padx=5, pady=5)
            
            entry = ttk.Entry(frame_totals, font=("Arial", 10), width=20)
            entry.insert(0, default)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.totals_entries[label] = entry

    def nueva_factura(self):
        try:
            # Clear existing fields if any
            self.cliente_combo.set('')
            for entry in self.entries.values():
                entry.delete(0, tk.END)
            
            # Clear products table
            for item in self.table.get_children():
                self.table.delete(item)
            
            # Reset totals
            for entry in self.totals_entries.values():
                entry.delete(0, tk.END)
                entry.insert(0, "0.00")
            
            # Set current date
            self.entries["Fecha"].delete(0, tk.END)
            self.entries["Fecha"].insert(0, datetime.datetime.now().strftime("%d/%m/%Y"))
            
            messagebox.showinfo("Éxito", "Nueva factura iniciada")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear nueva factura: {e}")

        # Estilo general
        style = ttk.Style()
        style.configure("TLabel", background="#FFC0CB", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10, "bold"))

        # Campos superiores
        frame_top = tk.Frame(self.root, bg="#FFC0CB")
        frame_top.pack(padx=10, pady=10, fill=tk.X)

        # Modificación: Agregar combobox para seleccionar cliente
        tk.Label(frame_top, text="Seleccionar Cliente", bg="#FFC0CB", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.cliente_combo = ttk.Combobox(frame_top, font=("Arial", 10), width=30, state="readonly")
        self.actualizar_lista_clientes()
        self.cliente_combo.grid(row=0, column=1, padx=5, pady=5)
        self.cliente_combo.bind("<<ComboboxSelected>>", self.cargar_datos_cliente)

        fields = [
            ("RUT", ""), ("Razón Social", ""),
            ("Giro", ""), ("Teléfono", ""),
            ("Dirección", ""), ("Comuna", ""),
            ("Ciudad", ""), ("Fecha", datetime.datetime.now().strftime("%d/%m/%Y"))
        ]

        self.entries = {}
        for i, (label, default) in enumerate(fields):
            tk.Label(frame_top, text=label, bg="#FFC0CB", font=("Arial", 10)).grid(row=(i+1) // 2, column=((i+1) % 2) * 2, sticky="w", padx=5, pady=5)
            entry = ttk.Entry(frame_top, font=("Arial", 10), width=30)
            entry.insert(0, default)
            entry.grid(row=(i+1) // 2, column=((i+1) % 2) * 2 + 1, padx=5, pady=5)
            self.entries[label] = entry

        # Tabla de productos
        frame_table = tk.Frame(self.root, bg="#FFC0CB")
        frame_table.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        columns = ["Código", "Cantidad", "Descripción", "Precio Unit.", "Total"]
        self.table = ttk.Treeview(frame_table, columns=columns, show="headings", height=10)
        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=100 if col != "Descripción" else 200)
        self.table.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Botones debajo de la tabla
        frame_buttons = tk.Frame(self.root, bg="#FFC0CB")
        frame_buttons.pack(padx=10, pady=10, fill=tk.X)

        btn_add = ttk.Button(frame_buttons, text="Agregar Producto", command=self.agregar_producto)
        btn_add.pack(side=tk.LEFT, padx=5, pady=5)

        btn_clear = ttk.Button(frame_buttons, text="Limpiar Productos", command=self.limpiar_tabla)
        btn_clear.pack(side=tk.LEFT, padx=5, pady=5)

        # Totales
        frame_totals = tk.Frame(self.root, bg="#FFC0CB")
        frame_totals.pack(padx=10, pady=10, fill=tk.X)

        totals = [
            ("Observación", ""), ("Total Neto", ""),
            ("IVA 19%", ""), ("TOTAL", "")
        ]

        self.totals_entries = {}
        for i, (label, default) in enumerate(totals):
            tk.Label(frame_totals, text=label, bg="#FFC0CB", font=("Arial", 10)).grid(row=i, column=0, sticky="w", padx=5, pady=5)
            entry = ttk.Entry(frame_totals, font=("Arial", 10), width=20)
            entry.insert(0, default)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.totals_entries[label] = entry

        # Botón para generar PDF
        btn_pdf = ttk.Button(self.root, text="Generar PDF", command=self.generar_pdf)
        btn_pdf.pack(pady=10)

        self.actualizar_totales()

    def actualizar_lista_clientes(self):
        try:
            conn = conectar_bd()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nombre FROM clientes")
                clientes = cursor.fetchall()
                self.cliente_combo['values'] = [cliente[1] for cliente in clientes]
        except Error as e:
            messagebox.showerror("Error", f"Error al cargar clientes: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def cargar_datos_cliente(self, event):
        nombre_cliente = self.cliente_combo.get()
        try:
            conn = conectar_bd()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT rfc, nombre, telefono, direccion, comuna, ciudad 
                    FROM clientes WHERE nombre = %s
                """, (nombre_cliente,))
                cliente = cursor.fetchone()
                
                if cliente:
                    self.entries["RUT"].delete(0, tk.END)
                    self.entries["RUT"].insert(0, cliente[0] or "")
                    self.entries["Razón Social"].delete(0, tk.END)
                    self.entries["Razón Social"].insert(0, cliente[1] or "")
                    self.entries["Teléfono"].delete(0, tk.END)
                    self.entries["Teléfono"].insert(0, cliente[2] or "")
                    self.entries["Dirección"].delete(0, tk.END)
                    self.entries["Dirección"].insert(0, cliente[3] or "")
                    self.entries["Comuna"].delete(0, tk.END)
                    self.entries["Comuna"].insert(0, cliente[4] or "")
                    self.entries["Ciudad"].delete(0, tk.END)
                    self.entries["Ciudad"].insert(0, cliente[5] or "")
        except Error as e:
            messagebox.showerror("Error", f"Error al cargar datos del cliente: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def agregar_producto(self):
        # Ventana emergente para agregar producto
        def confirmar_agregar():
            seleccion = producto_combo.get()
            if not seleccion or not entry_cantidad.get().strip():
                messagebox.showerror("Error", "Debe seleccionar un producto y especificar la cantidad.")
                return

            codigo = seleccion.split(" - ")[0].strip()
            cantidad = entry_cantidad.get().strip()
            
            try:
                conn = conectar_bd()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT codigo, nombre, descripcion, precio 
                        FROM productos WHERE codigo = %s
                    """, (codigo,))
                    producto = cursor.fetchone()
                    
                    if producto and producto[3] is not None:
                        cantidad = int(cantidad)
                        precio_unit = float(producto[3])
                        total = cantidad * precio_unit
                        
                        self.table.insert("", "end", values=(
                            codigo, cantidad, producto[2],
                            f"${precio_unit:.2f}", f"${total:.2f}"
                        ))
                        self.actualizar_totales()
                        popup.destroy()
                    else:
                        messagebox.showerror("Error", "Producto no encontrado o precio no válido.")
            except ValueError:
                messagebox.showerror("Error", "La cantidad debe ser un número entero.")
            except Error as e:
                messagebox.showerror("Error", f"Error al agregar producto: {e}")
            finally:
                if 'conn' in locals() and conn.is_connected():
                    cursor.close()
                    conn.close()

        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title("Agregar Producto")
        popup.geometry("400x300")
        popup.configure(bg="#FFC0CB")

        # Add product selection combobox
        try:
            conn = conectar_bd()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT codigo, nombre FROM productos")
                productos_list = cursor.fetchall()
                producto_combo = ttk.Combobox(popup, state="readonly")
                producto_combo['values'] = [f"{p[0]} - {p[1]}" for p in productos_list]
        except Error as e:
            messagebox.showerror("Error", f"Error al cargar productos: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

        # Combobox para seleccionar producto
        tk.Label(popup, text="Seleccionar Producto", bg="#FFC0CB", font=("Arial", 10)).pack(pady=5)
        producto_combo = ttk.Combobox(popup, state="readonly")
        producto_combo.pack(pady=5)

        # Obtener la lista de productos
        #producto_combo['values'] = [f"{codigo} - {productos[codigo]['nombre']}" for codigo in productos]
        def cargar_datos_producto(event):
            seleccion = producto_combo.get()
            if seleccion:
                codigo = seleccion.split(" - ")[0].strip()
                try:
                    conn = conectar_bd()
                    if conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                                SELECT descripcion, precio, cantidad 
                                FROM productos 
                                WHERE codigo = %s
                            """, (codigo,))
                        producto = cursor.fetchone()
                        if producto:
                            entry_descripcion.configure(state="normal")
                            entry_descripcion.delete(0, tk.END)
                            entry_descripcion.insert(0, producto[0])
                            entry_descripcion.configure(state="readonly")
                                
                            entry_precio.configure(state="normal")
                            entry_precio.delete(0, tk.END)
                            entry_precio.insert(0, f"{float(producto[1]):.2f}")
                            entry_precio.configure(state="readonly")
                                
                                # Clear and enable cantidad field
                            entry_cantidad.delete(0, tk.END)
                            entry_cantidad.configure(state="normal")
                                
                                # Show available quantity label
                            lbl_disponible.configure(text=f"Disponible: {producto[2]}")
                except Error as e:
                    messagebox.showerror("Error", f"Error al cargar producto: {e}")
                finally:
                    if 'conn' in locals() and conn.is_connected():
                        cursor.close()
                        conn.close()
        
            def confirmar_agregar():
                seleccion = producto_combo.get()
                cantidad = entry_cantidad.get().strip()
                
                if not seleccion or not cantidad:
                    messagebox.showerror("Error", "Complete todos los campos")
                    return
                    
                try:
                    cantidad = int(cantidad)
                    if cantidad <= 0:
                        messagebox.showerror("Error", "Cantidad debe ser mayor a 0")
                        return
                        
                    codigo = seleccion.split(" - ")[0].strip()
                    precio = float(entry_precio.get())
                    total = cantidad * precio
                    
                    self.table.insert("", "end", values=(
                        codigo,
                        cantidad,
                        entry_descripcion.get(),
                        f"${precio:.2f}",
                        f"${total:.2f}"
                    ))
                    self.actualizar_totales()
                    popup.destroy()
                    
                except ValueError:
                    messagebox.showerror("Error", "Cantidad debe ser un número entero")
        
            popup = tk.Toplevel(self.root)
            popup.title("Agregar Producto")
            popup.geometry("400x350")
            popup.configure(bg=COLOR_FONDO)
        
            # Product selection
            tk.Label(popup, text="Seleccionar Producto", 
                    bg=COLOR_FONDO, font=("Arial", 10)).pack(pady=5)
            producto_combo = ttk.Combobox(popup, state="readonly")
            producto_combo.pack(pady=5)
        
            # Quantity section with available label
            frame_cantidad = tk.Frame(popup, bg=COLOR_FONDO)
            frame_cantidad.pack(pady=5, fill=tk.X)
            
            tk.Label(frame_cantidad, text="Cantidad", 
                    bg=COLOR_FONDO, font=("Arial", 10)).pack(pady=5)
            entry_cantidad = ttk.Entry(frame_cantidad)
            entry_cantidad.pack(pady=5)
            
            lbl_disponible = tk.Label(frame_cantidad, text="", 
                                     bg=COLOR_FONDO, fg="blue", font=("Arial", 9))
            lbl_disponible.pack()
        
            # Description and price fields
            tk.Label(popup, text="Descripción", 
                    bg=COLOR_FONDO, font=("Arial", 10)).pack(pady=5)
            entry_descripcion = ttk.Entry(popup, state="readonly")
            entry_descripcion.pack(pady=5)
        
            tk.Label(popup, text="Precio Unit.", 
                    bg=COLOR_FONDO, font=("Arial", 10)).pack(pady=5)
            entry_precio = ttk.Entry(popup, state="readonly")
            entry_precio.pack(pady=5)
        
            # Load products
            try:
                conn = conectar_bd()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT codigo, nombre FROM productos WHERE cantidad > 0")
                    productos_list = cursor.fetchall()
                    producto_combo['values'] = [f"{p[0]} - {p[1]}" for p in productos_list]
            except Error as e:
                messagebox.showerror("Error", f"Error al cargar productos: {e}")
            finally:
                if 'conn' in locals() and conn.is_connected():
                    cursor.close()
                    conn.close()
        
            producto_combo.bind("<<ComboboxSelected>>", cargar_datos_producto)
        
            tk.Button(popup, text="Agregar",
                     command=confirmar_agregar,
                     bg=COLOR_BOTON, fg=COLOR_TEXTO_BOTON).pack(pady=10)
        
        tk.Label(popup, text="Cantidad", 
                bg=COLOR_FONDO, font=("Arial", 10)).pack(pady=5)
        entry_cantidad = ttk.Entry(popup)
        entry_cantidad.pack(pady=5)
        
        tk.Label(popup, text="Descripción", 
                bg=COLOR_FONDO, font=("Arial", 10)).pack(pady=5)
        entry_descripcion = ttk.Entry(popup)
        entry_descripcion.pack(pady=5)
        
        tk.Label(popup, text="Precio Unit.", 
                bg=COLOR_FONDO, font=("Arial", 10)).pack(pady=5)
        entry_precio = ttk.Entry(popup)
        entry_precio.pack(pady=5)
        
        tk.Button(popup, text="Agregar",
                    command=lambda: confirmar_agregar(producto_combo, entry_cantidad,
                                                     entry_descripcion, entry_precio),
                     bg=COLOR_BOTON, fg=COLOR_TEXTO_BOTON).pack(pady=10)

        producto_combo.bind("<<ComboboxSelected>>", cargar_datos_producto)

        tk.Label(popup, text="Cantidad", bg="#FFC0CB", font=("Arial", 10)).pack(pady=5)
        entry_cantidad = ttk.Entry(popup)
        entry_cantidad.pack(pady=5)

        tk.Label(popup, text="Descripción", bg="#FFC0CB", font=("Arial", 10)).pack(pady=5)
        entry_descripcion = ttk.Entry(popup, state="readonly")
        entry_descripcion.pack(pady=5)

        tk.Label(popup, text="Precio Unit.", bg="#FFC0CB", font=("Arial", 10)).pack(pady=5)
        entry_precio = ttk.Entry(popup, state="readonly")
        entry_precio.pack(pady=5)

        tk.Button(popup, text="Agregar", command=confirmar_agregar, bg="#FF69B4", fg="white").pack(pady=10)

    def limpiar_tabla(self):
        for item in self.table.get_children():
            self.table.delete(item)
        self.actualizar_totales()

    def actualizar_totales(self):
        total_neto = 0.0
        for item in self.table.get_children():
            valores = self.table.item(item, 'values')
            total_str = valores[4].replace('$', '')
            try:
                total_neto += float(total_str)
            except ValueError:
                pass  # Ignorar valores inválidos
        iva = total_neto * 0.19
        total = total_neto + iva

        self.totals_entries["Total Neto"].delete(0, tk.END)
        self.totals_entries["Total Neto"].insert(0, f"${total_neto:.2f}")

        self.totals_entries["IVA 19%"].delete(0, tk.END)
        self.totals_entries["IVA 19%"].insert(0, f"${iva:.2f}")

        self.totals_entries["TOTAL"].delete(0, tk.END)
        self.totals_entries["TOTAL"].insert(0, f"${total:.2f}")

    def generar_pdf(self):
        global contador_facturas
        # Obtener los datos de los campos superiores
        rut = self.entries["RUT"].get().strip()
        razon_social = self.entries["Razón Social"].get().strip()
        giro = self.entries["Giro"].get().strip()
        telefono = self.entries["Teléfono"].get().strip()
        direccion = self.entries["Dirección"].get().strip()
        comuna = self.entries["Comuna"].get().strip()
        ciudad = self.entries["Ciudad"].get().strip()
        fecha = self.entries["Fecha"].get().strip()
        observacion = self.totals_entries["Observación"].get().strip()
        total_neto = self.totals_entries["Total Neto"].get().strip()
        iva = self.totals_entries["IVA 19%"].get().strip()
        total = self.totals_entries["TOTAL"].get().strip()

        # Validar que haya productos
        if not self.table.get_children():
            messagebox.showerror("Error", "No hay productos agregados a la factura.")
            return

        try:
            conn = conectar_bd()
            if conn:
                cursor = conn.cursor()
                
                # Insert factura
                cursor.execute("""
                    INSERT INTO facturas (fecha, cliente_id, total) 
                    VALUES (%s, (SELECT id FROM clientes WHERE nombre = %s), %s)
                    RETURNING id
                """, (self.entries["Fecha"].get(),
                     self.entries["Razón Social"].get(),
                     self.totals_entries["TOTAL"].get().replace('$', '')))
                
                factura_id = cursor.fetchone()[0]
                
                # Insert detalle_facturas
                for item in self.table.get_children():
                    valores = self.table.item(item)['values']
                    cursor.execute("""
                        INSERT INTO detalle_facturas 
                        (factura_id, producto_id, cantidad, precio_unitario, total)
                        VALUES (%s, 
                                (SELECT id FROM productos WHERE codigo = %s),
                                %s, %s, %s)
                    """, (factura_id, valores[0], valores[1],
                         valores[3].replace('$', ''),
                         valores[4].replace('$', '')))
                
                conn.commit()
                
                # Generate PDF
                self.generar_pdf_archivo(factura_id)
                
        except Error as e:
            messagebox.showerror("Error", f"Error al guardar factura: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

        # Crear el PDF
        nombre_archivo = f"Factura_{rut}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        c = canvas.Canvas(nombre_archivo, pagesize=letter)
        width, height = letter

        # Título
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - 50, "Factura")

        # Información de la empresa o cliente
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 80, f"RUT: {rut}")
        c.drawString(50, height - 100, f"Razón Social: {razon_social}")
        c.drawString(50, height - 120, f"Giro: {giro}")
        c.drawString(50, height - 140, f"Teléfono: {telefono}")
        c.drawString(50, height - 160, f"Dirección: {direccion}")
        c.drawString(50, height - 180, f"Comuna: {comuna}")
        c.drawString(50, height - 200, f"Ciudad: {ciudad}")
        c.drawString(50, height - 220, f"Fecha: {fecha}")

        # Encabezado de la tabla
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 250, "Código")
        c.drawString(150, height - 250, "Cantidad")
        c.drawString(250, height - 250, "Descripción")
        c.drawString(500, height - 250, "Precio Unit.")
        c.drawString(600, height - 250, "Total")
        y = height - 270
        c.setFont("Helvetica", 12)

        # Datos de la tabla
        productos_factura = []
        for item in self.table.get_children():
            valores = self.table.item(item, 'values')
            c.drawString(50, y, valores[0])
            c.drawString(150, y, str(valores[1]))
            c.drawString(250, y, valores[2])
            c.drawString(500, y, valores[3])
            c.drawString(600, y, valores[4])
            productos_factura.append({
                "codigo": valores[0],
                "cantidad": valores[1],
                "descripcion": valores[2],
                "precio_unitario": valores[3],
                "total": valores[4]
            })
            y -= 20
            if y < 100:
                c.showPage()
                y = height - 50

        # Totales
        c.setFont("Helvetica-Bold", 12)
        c.drawString(400, y - 10, "Total Neto:")
        c.drawString(500, y - 10, total_neto)
        c.drawString(400, y - 30, "IVA 19%:")
        c.drawString(500, y - 30, iva)
        c.drawString(400, y - 50, "TOTAL:")
        c.drawString(500, y - 50, total)

        # Observación
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y - 80, "Observación:")
        c.setFont("Helvetica", 12)
        c.drawString(150, y - 80, observacion)

        # Guardar el PDF
        try:
            c.save()
            messagebox.showinfo("Éxito", f"Factura generada y guardada como {nombre_archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el PDF:\n{e}")
            return

        # Crear una entrada de factura
        factura = {
            "numero": contador_facturas,
            "fecha": fecha,
            "cliente": razon_social,
            "total": total,
            "productos": productos_factura
        }

        # Agregar la factura a la lista global
        facturas.append(factura)

        # Incrementar el contador de facturas
        contador_facturas += 1

# Ventana para listar facturas generadas
class FacturasListWindow:
    def __init__(self, root):
        self.root = tk.Toplevel(root)
        self.root.title("Facturas Generadas")
        self.root.geometry("600x400")
        self.root.configure(bg=COLOR_FONDO)

        # Título
        title = tk.Label(self.root, text="Facturas Generadas", font=("Arial", 18, "bold"),
                         bg=COLOR_FONDO, fg=COLOR_BOTON)
        title.pack(pady=10)

        # Lista de facturas
        self.tree = ttk.Treeview(self.root, columns=("Número", "Fecha", "Cliente", "Total"), show='headings')
        self.tree.heading("Número", text="Número")
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Cliente", text="Cliente")
        self.tree.heading("Total", text="Total")
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        # Botón para visualizar factura
        btn_view = tk.Button(self.root, text="Visualizar Factura", width=20, height=2,
                             bg=COLOR_BOTON, fg=COLOR_TEXTO_BOTON, command=self.visualizar_factura)
        btn_view.pack(pady=10)

        self.cargar_facturas()

    def cargar_facturas(self):
        # Limpiar la tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Insertar facturas
        for idx, factura in enumerate(facturas):
            self.tree.insert("", "end", iid=idx, values=(factura["numero"], factura["fecha"],
                                                         factura["cliente"], factura["total"]))

    def visualizar_factura(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Seleccione una factura para visualizar.")
            return
        selected_item = selected_items[0]
        factura = facturas[int(selected_item)]
        InvoiceView(self.root, factura)

# Clase para visualizar una factura
class InvoiceView:
    def __init__(self, root, factura):
        self.root = tk.Toplevel(root)
        self.root.title("Detalle de la Factura")
        self.root.geometry("500x550")
        self.root.configure(bg=COLOR_FONDO)
        self.factura = factura  # Guardar la factura para usarla al generar el PDF

        # Título
        title = tk.Label(self.root, text="Detalle de la Factura", font=("Arial", 18, "bold"),
                         bg=COLOR_FONDO, fg=COLOR_BOTON)
        title.pack(pady=10)

        # Información de la factura
        info_frame = tk.Frame(self.root, bg=COLOR_FONDO)
        info_frame.pack(pady=5)

        tk.Label(info_frame, text=f"Número de Factura: {factura['numero']}",
                 bg=COLOR_FONDO, fg=COLOR_BOTON).grid(row=0, column=0, padx=5, sticky='w')
        tk.Label(info_frame, text=f"Fecha: {factura['fecha']}",
                 bg=COLOR_FONDO, fg=COLOR_BOTON).grid(row=0, column=1, padx=5, sticky='w')

        # Información del cliente
        cliente_label = tk.Label(self.root, text=f"Cliente: {factura['cliente']}",
                                 bg=COLOR_FONDO, fg=COLOR_BOTON, font=("Arial", 12))
        cliente_label.pack(pady=5)

        # Obtener RFC del cliente
        rfc_cliente = self.obtener_rfc_cliente(factura['cliente'])
        rfc_label = tk.Label(self.root, text=f"RFC: {rfc_cliente}",
                             bg=COLOR_FONDO, fg=COLOR_BOTON, font=("Arial", 12))
        rfc_label.pack(pady=5)

        # Tabla de productos
        tree = ttk.Treeview(self.root, columns=("Producto", "Precio", "Cantidad", "Total"), show='headings')
        tree.heading("Producto", text="Producto")
        tree.heading("Precio", text="Precio")
        tree.heading("Cantidad", text="Cantidad")
        tree.heading("Total", text="Total")
        tree.pack(pady=10, fill=tk.BOTH, expand=True)

        # Insertar productos en la tabla
        for producto in factura["productos"]:
            tree.insert("", "end", values=(producto["descripcion"], producto["precio_unitario"],
                                           producto["cantidad"], producto["total"]))

        # Total de la factura
        total_label = tk.Label(self.root, text=f"Total: {factura['total']}",
                               font=("Arial", 14), bg=COLOR_FONDO, fg=COLOR_BOTON)
        total_label.pack(pady=5)

        # Botón para descargar PDF
        btn_pdf = tk.Button(self.root, text="Descargar PDF", width=20, height=2,
                            bg=COLOR_BOTON, fg=COLOR_TEXTO_BOTON, command=self.descargar_pdf)
        btn_pdf.pack(pady=10)

    def descargar_pdf(self):
        # Generar el PDF de la factura utilizando reportlab
        factura = self.factura
        nombre_archivo = f"Factura_{factura['numero']}.pdf"

        # Crear el lienzo del PDF
        c = canvas.Canvas(nombre_archivo, pagesize=letter)
        width, height = letter

        # Título
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - 50, "Detalle de la Factura")

        # Información de la factura
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Número de Factura: {factura['numero']}")
        c.drawString(300, height - 80, f"Fecha: {factura['fecha']}")

        # Información del cliente
        c.drawString(50, height - 110, f"Cliente: {factura['cliente']}")
        c.drawString(50, height - 130, f"RFC: {self.obtener_rfc_cliente(factura['cliente'])}")

        # Tabla de productos
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 160, "Descripción")
        c.drawString(300, height - 160, "Precio")
        c.drawString(400, height - 160, "Cantidad")
        c.drawString(500, height - 160, "Total")

        c.setFont("Helvetica", 12)
        y = height - 180
        for producto in factura["productos"]:
            c.drawString(50, y, producto["descripcion"])
            c.drawString(300, y, producto["precio_unitario"])
            c.drawString(400, y, str(producto["cantidad"]))
            c.drawString(500, y, producto["total"])
            y -= 20
            if y < 100:
                c.showPage()
                y = height - 50

        # Totales
        c.setFont("Helvetica-Bold", 12)
        # Extraer solo el monto del total
        c.drawString(400, y - 20, f"Total: {factura['total']}")

        # Guardar el PDF
        try:
            c.save()
            messagebox.showinfo("Éxito", f"Factura guardada como {nombre_archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el PDF:\n{e}")

    def obtener_rfc_cliente(self, nombre_cliente):
        for val in clientes.values():
            if val["nombre"] == nombre_cliente:
                return val.get("rfc", "N/A")
        return "N/A"

# Ejecutar la aplicación
if __name__ == "__main__":
    # Verificar si reportlab está instalado
    try:
        from reportlab.pdfgen import canvas
    except ImportError:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", "La librería reportlab no está instalada. Por favor, instálala antes de continuar.")
        exit()

    root = tk.Tk()
    app = App(root)
    root.mainloop()
