import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
import datetime

# Configuración de la base de datos
db_config = {
    "host": "localhost",
    "user": "tu_usuario",  # Cambia a tu usuario
    "password": "tu_contraseña",  # Cambia a tu contraseña
    "database": "facturacion"  # Cambia al nombre de tu base de datos
}

# Conexión a la base de datos
def conectar_bd():
    return mysql.connector.connect(**db_config)

# Colores para la interfaz
COLOR_FONDO = "#ffe6f0"
COLOR_BOTON = "#ff66b2"
COLOR_TEXTO_BOTON = "#ffffff"
COLOR_CAMPO = "#fff0f5"

# Ventana principal
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
        messagebox.showinfo("Función", "Función no implementada todavía.")

# Ventana de Registro de Usuario
class RegisterWindow:
    def __init__(self, root):
        self.root = tk.Toplevel(root)
        self.root.title("Registro de Usuario")
        self.root.geometry("300x450")
        self.root.configure(bg=COLOR_FONDO)

        title = tk.Label(self.root, text="Registro de Usuario", font=("Arial", 16, "bold"),
                         bg=COLOR_FONDO, fg=COLOR_BOTON)
        title.pack(pady=10)

        self.entry_usuario = self.crear_campo("Usuario")
        self.entry_contrasena = self.crear_campo("Contraseña", show="*")
        self.entry_confirmar_contrasena = self.crear_campo("Confirmar Contraseña", show="*")
        self.entry_correo = self.crear_campo("Correo")
        self.entry_telefono = self.crear_campo("Teléfono")

        btn_register = tk.Button(self.root, text="Registrar", width=15, height=2,
                                 bg=COLOR_BOTON, fg=COLOR_TEXTO_BOTON, command=self.registrar)
        btn_register.pack(pady=20)

    def crear_campo(self, texto, show=None):
        label = tk.Label(self.root, text=texto, bg=COLOR_FONDO, fg=COLOR_BOTON)
        label.pack(pady=5)
        entry = tk.Entry(self.root, show=show, bg=COLOR_CAMPO, fg="black")
        entry.pack(pady=5)
        return entry

    def registrar(self):
        usuario = self.entry_usuario.get().strip()
        contrasena = self.entry_contrasena.get().strip()
        confirmar_contrasena = self.entry_confirmar_contrasena.get().strip()
        correo = self.entry_correo.get().strip()
        telefono = self.entry_telefono.get().strip()

        if not usuario or not contrasena or not confirmar_contrasena or not correo or not telefono:
            messagebox.showerror("Error", "Por favor, complete todos los campos.")
            return
        if contrasena != confirmar_contrasena:
            messagebox.showerror("Error", "Las contraseñas no coinciden.")
            return

        try:
            conn = conectar_bd()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (usuario, contrasena, correo, telefono) VALUES (%s, %s, %s, %s)",
                           (usuario, contrasena, correo, telefono))
            conn.commit()
            messagebox.showinfo("Éxito", "Usuario registrado exitosamente.")
            self.root.destroy()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"No se pudo registrar el usuario: {e}")
        finally:
            cursor.close()
            conn.close()

# Ventana de Inicio de Sesión
class LoginWindow:
    def __init__(self, root):
        self.root = tk.Toplevel(root)
        self.root.title("Inicio de Sesión")
        self.root.geometry("300x300")
        self.root.configure(bg=COLOR_FONDO)

        title = tk.Label(self.root, text="Inicio de Sesión", font=("Arial", 16, "bold"),
                         bg=COLOR_FONDO, fg=COLOR_BOTON)
        title.pack(pady=10)

        self.entry_usuario = self.crear_campo("Usuario")
        self.entry_contrasena = self.crear_campo("Contraseña", show="*")

        btn_login = tk.Button(self.root, text="Iniciar Sesión", width=15, height=2,
                              bg=COLOR_BOTON, fg=COLOR_TEXTO_BOTON, command=self.login)
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
            messagebox.showerror("Error", "Ingrese el usuario y la contraseña.")
            return

        try:
            conn = conectar_bd()
            cursor = conn.cursor()
            cursor.execute("SELECT contrasena FROM usuarios WHERE usuario = %s", (usuario,))
            resultado = cursor.fetchone()
            if resultado and resultado[0] == contrasena:
                messagebox.showinfo("Éxito", "Inicio de sesión exitoso.")
                self.root.destroy()
                MainScreen(self.root.master)
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error al iniciar sesión: {e}")
        finally:
            cursor.close()
            conn.close()

# Pantalla Principal
class MainScreen:
    def __init__(self, root):
        self.root = tk.Toplevel(root)
        self.root.title("Pantalla Principal - Factgre")
        self.root.geometry("400x350")
        self.root.configure(bg=COLOR_FONDO)

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
        messagebox.showinfo("Función", "Gestión de Productos no implementada todavía.")

    def gestion_clientes(self):
        messagebox.showinfo("Función", "Gestión de Clientes no implementada todavía.")

    def facturacion(self):
        messagebox.showinfo("Función", "Facturación no implementada todavía.")

    def visualizar_facturas(self):
        messagebox.showinfo("Función", "Visualización de Facturas no implementada todavía.")

# Ejecución de la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
