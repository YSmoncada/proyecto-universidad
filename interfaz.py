import tkinter as tk
from tkinter import ttk, messagebox
from controlador import *
from datetime import datetime, date


class VentanaPrincipal:
    FONDO = "azure2"
    BOTON1 = "medium spring green"
    BOTON2 = "dodger blue"
    BOTON3 = "gold"
    BOTON4 = "tomato"
    TEXTO = "slate blue4"
    ENTRADA_BG = "white"

    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Sistema de Inventario, Ventas y Cálculo de Impuesto")
        self.ventana.geometry("1600x860")
        self.ventana.configure(bg=self.FONDO)
        self._crear_componentes()

    def _crear_componentes(self):
        tk.Label(self.ventana, text="Sistema de Inventario y Ventas", font=("Segoe UI", 20, "bold"),
                 bg=self.FONDO, fg=self.TEXTO).pack(pady=40)

        frame = tk.Frame(self.ventana, bg=self.FONDO)
        frame.pack(pady=10)

        botones = [
            ("Agregar a Inventario", self.ventana_agregar_inventario, self.BOTON1),
            ("Ver Inventario", self.inventario, self.BOTON3),
            ("Agregar Ventas y Cálculo de Impuesto", self.agregar_venta, self.BOTON2),
            ("Historial de Ventas", self.ventas, self.BOTON4),
        ]

        for texto, accion, color in botones:
            tk.Button(frame, text=texto, command=accion, bg=color, fg="white",
                      font=("Segoe UI", 12, "bold"), width=40, height=2).pack(pady=10)

    def ventana_agregar_inventario(self):
        agregar_inventario = tk.Toplevel()
        agregar_inventario.title("Agregar Artículos al Inventario")
        agregar_inventario.geometry("520x450")
        agregar_inventario.configure(bg=self.FONDO)

        tk.Label(agregar_inventario, text="Registrar Producto", font=("Segoe UI", 14, "bold"),
                 bg=self.FONDO, fg=self.TEXTO).pack(pady=10)

        campos = {}
        etiquetas = ["Nombre", "Código", "Vencimiento", "Precio", "Cantidad", "Medida"]
        for i, texto in enumerate(etiquetas):
            tk.Label(agregar_inventario, text=texto, bg=self.FONDO, fg=self.TEXTO,
                     font=("Segoe UI", 10)).place(x=30, y=50 + i*40)
            entry = tk.Entry(agregar_inventario, width=30, font=("Segoe UI", 10), bg=self.ENTRADA_BG)
            entry.place(x=120, y=50 + i*40)
            campos[texto.lower()] = entry

        def add_placeholder(entry, placeholder):
            def on_focus_in(event):
                if entry.get() == placeholder:
                    entry.delete(0, tk.END)
                    entry.config(fg='black')
            def on_focus_out(event):
                if not entry.get():
                    entry.insert(0, placeholder)
                    entry.config(fg='gray')
            entry.insert(0, placeholder)
            entry.config(fg='gray')
            entry.bind('<FocusIn>', on_focus_in)
            entry.bind('<FocusOut>', on_focus_out)

        vencimiento_entry = campos["vencimiento"]
        add_placeholder(vencimiento_entry, "dd-mm-aaaa")

        
        unidades = ["Litros", "Mililitros", "Kilos", "Gramos"]
        unidades_variable = tk.StringVar(value="Litros")
        

        tk.Label(agregar_inventario, text="Unidad de Medida", bg=self.FONDO, fg=self.TEXTO,
                 font=("Segoe UI", 10)).place(x=30, y=50 + len(etiquetas)*40)
        
        unidad_menu = tk.OptionMenu(agregar_inventario, unidades_variable, *unidades)
        unidad_menu.place(x=160, y=50 + len(etiquetas)*40)

        def guardar():
            try:
                nombre = campos["nombre"].get().strip().title()
                codigo = campos["código"].get().strip()
                vencimiento = campos["vencimiento"].get().strip()
                precio = campos["precio"].get().strip().replace(",", ".")
                cantidad = campos["cantidad"].get().strip()
                medida = campos["medida"].get().strip()
               

                if not nombre or not codigo or not vencimiento or not precio or not cantidad or not medida:
                    messagebox.showerror("Error", "Todos los campos deben estar completos.")
                    return

                try:
                    vencimiento = datetime.strptime(vencimiento, "%d-%m-%Y").date()
                except ValueError:
                    messagebox.showerror("Error", "La fecha de vencimiento debe estar en formato dd-mm-aaaa.")
                    return

                try:
                    precio = float(precio)
                except ValueError:
                    messagebox.showerror("Error", "El precio debe ser un número válido (usa punto o coma como separador decimal).")
                    return

                try:
                    cantidad = int(cantidad)
                except ValueError:
                    messagebox.showerror("Error", "La cantidad debe ser un número entero.")
                    campos["precio"].delete(0, tk.END)
                    campos["precio"].focus_set()
                    return

                agregar_producto(nombre, codigo, vencimiento, precio, cantidad, medida, unidades_variable.get())
                messagebox.showinfo("Producto registrado correctamente",
                            "El producto ha sido registrado exitosamente.")
                for campo in campos.values():
                    campo.delete(0, tk.END)
                campos["nombre"].focus_set()

            except Exception as e:
                messagebox.showerror("Error inesperado", str(e))

        tk.Button(agregar_inventario, text="Guardar", command=guardar, bg=self.BOTON1, fg="white",
                  font=("Segoe UI", 10, "bold")).place(x=200, y=350)

    def inventario(self):
        inventario_stock = tk.Toplevel()
        inventario_stock.title("Inventario")
        inventario_stock.geometry("1600x860")
        inventario_stock.configure(bg=self.FONDO)

        tk.Label(inventario_stock, text="Inventario de Productos", font=("Segoe UI", 14, "bold"),
                 bg=self.FONDO, fg=self.TEXTO).pack(pady=10)

        columnas = ("Nombre", "Código", "Vencimiento / Días restantes", "Precio", "Cantidad", "Medida", "Unidad")
        tabla = ttk.Treeview(inventario_stock, columns=columnas, show="headings", height=30)
        for col in columnas:
            tabla.heading(col, text=col)
            tabla.column(col, anchor="center")

        barra_desplazamiento = ttk.Scrollbar(inventario_stock, orient="vertical", command=tabla.yview)
        tabla.configure(yscroll=barra_desplazamiento.set)
        barra_desplazamiento.pack(side="right", fill="y")
        tabla.pack(fill="both", expand=True)

        def actualizar_tabla():
            tabla.delete(*tabla.get_children())
            for producto in obtener_productos():
                try:
                    vencimiento_date = producto.vencimiento
                    hoy = date.today()
                    dias_restantes = (vencimiento_date - hoy).days

                    if dias_restantes < 0:
                        vencimiento = f"{vencimiento_date.strftime('%d-%m-%Y')} (¡VENCIDO!)"
                    else:
                        vencimiento = f"{vencimiento_date.strftime('%d-%m-%Y')} ({dias_restantes} días restantes)"
                except Exception as e:
                    vencimiento = f"Error: {e}"

                tabla.insert('', 'end', values=(
                    producto.nombre, producto.codigo, vencimiento, f"COP {producto.precio:,.2f}",  # Formato COP
                    producto.cantidad, producto.medida, producto.unidad))

        def eliminar_producto_evento():
            try:
                seleccion = tabla.selection()
                if not seleccion:
                    messagebox.showwarning("Advertencia", "Por favor selecciona un producto para eliminar.", parent=inventario_stock)
                    return

                valores = tabla.item(seleccion[0], "values")
                codigo = valores[1]

                eliminado = eliminar_producto_por_codigo(codigo)
                if eliminado:
                    messagebox.showinfo("Producto Eliminado", f"Producto con el código {codigo} eliminado correctamente.")
                else:
                    messagebox.showerror("Error", f"No se encontró un producto con el código {codigo}.")
                actualizar_tabla()

                tabla.focus_set()

            except Exception as e:
                messagebox.showerror("Error inesperado", f"Ocurrió un error inesperado al eliminar: {e}")

        actualizar_tabla()

        tk.Button(inventario_stock, text="Eliminar Producto", command=lambda: eliminar_producto_evento(), bg=self.BOTON1, fg="white",
                  font=("Segoe UI", 15, "bold")).place(x=600, y=550)

    def agregar_venta(self):
        ventana_ventas = tk.Toplevel()
        ventana_ventas.title("Registrar Ventas y Calcular Impuestos")
        ventana_ventas.geometry("420x300")
        ventana_ventas.configure(bg=self.FONDO)

        tk.Label(ventana_ventas, text="Registrar Venta", font=("Segoe UI", 14, "bold"),
                 bg=self.FONDO, fg=self.TEXTO).pack(pady=10)

        campos = {}
        etiquetas = ["Nombre", "Cantidad", "Medida"]
        for i, texto in enumerate(etiquetas):
            tk.Label(ventana_ventas, text=texto, bg=self.FONDO, fg=self.TEXTO,
                     font=("Segoe UI", 10)).place(x=30, y=50 + i*40)
            entry = tk.Entry(ventana_ventas, width=30, font=("Segoe UI", 10), bg=self.ENTRADA_BG)
            entry.place(x=120, y=50 + i*40)
            campos[texto.lower()] = entry

        unidades = ["Litros", "Mililitros", "Kilos", "Gramos"]
        unidades_variable=tk.StringVar(value="Litros")
        

        tk.Label(ventana_ventas, text="Unidad de Medida", bg=self.FONDO, fg=self.TEXTO,
                 font=("Segoe UI", 10)).place(x=30, y=50 + len(etiquetas)*40)
        unidad_menu = tk.OptionMenu(ventana_ventas, unidades_variable, *unidades)
        unidad_menu.place(x=160, y=50 + len(etiquetas)*40)

        def registrar_venta():
            try:
                nombre = campos["nombre"].get().strip()
                cantidad = int(campos["cantidad"].get().strip())
                medida = campos["medida"].get().strip()
                unidad = unidades_variable.get().strip()

                productos = obtener_productos()
                producto_encontrado = None

                for p in productos:
                    if p.nombre.lower() == nombre.lower():
                        producto_encontrado = p
                        break

                if not producto_encontrado:
                    messagebox.showerror("Producto no encontrado",
                                         f"El producto '{nombre}' no se encuentra ingresado en el inventario.")
                    return

                if producto_encontrado.unidad.lower() != unidad.lower():
                    messagebox.showerror("Unidad incorrecta",
                                          f"No tienes ningun producto en esta presentacion")
                    return

                if cantidad > producto_encontrado.cantidad:
                    messagebox.showerror("Cantidad insuficiente",
                                         f"No tienes suficientes productos en el inventario para realizar la venta. Disponible: {producto_encontrado.cantidad}")
                    return

                vender_producto(nombre, cantidad, medida, unidades_variable.get())
                messagebox.showinfo("Venta registrada con éxito",
                                     "La venta ha sido registrada exitosamente.")
                ventana_ventas.destroy()
                self.ventas()

            except ValueError:
                messagebox.showerror("Error", "por favor llenar los campos requeridos para registrar la venta.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        
        tk.Button(ventana_ventas, text="Registrar Venta", command=registrar_venta, bg=self.BOTON2, fg="white", font=("Segoe UI", 10, "bold")).place(x=130, y=200)


    def ventas(self):
        tabla_ventas = tk.Toplevel()
        tabla_ventas.title("Historial de Ventas")
        tabla_ventas.geometry("1600x860")
        tabla_ventas.configure(bg=self.FONDO)

        tk.Label(tabla_ventas, text="Historial de Ventas", font=("Segoe UI", 14, "bold"),
                 bg=self.FONDO, fg=self.TEXTO).pack(pady=10)

        columnas = ("Producto", "Cantidad", "Medida", "Unidad", "Fecha","Valor Unitario","total")
        tabla = ttk.Treeview(tabla_ventas, columns=columnas, show="headings", height=30)
        for col in columnas:
            tabla.heading(col, text=col)
            tabla.column(col, anchor="center")

        barra_desplazamiento = ttk.Scrollbar(tabla_ventas, orient="vertical", command=tabla.yview)
        tabla.configure(yscroll=barra_desplazamiento.set)
        barra_desplazamiento.pack(side="right", fill="y")
        tabla.pack(fill="both", expand=True)

        def actualizar_tabla():
                tabla.delete(*tabla.get_children())
                for venta in obtener_ventas():
                    producto = obtener_producto_por_nombre(venta["nombre"])
                    precio_venta = producto.precio * venta["cantidad"] if producto else 0
                    tabla.insert('', 'end', values=(
                        venta["nombre"], venta["cantidad"], venta["medida"], venta["unidad"],
                        venta["fecha"], f"COP {producto.precio:,.2f}" if producto else "N/A", f"COP {precio_venta:,.2f}"))
        
        actualizar_tabla()
        
        def calcular_impuesto():
            try:
                total = obtener_ventas_totales()
                impuesto = calcular_impuesto_anual(total)
                messagebox.showinfo("Impuesto Anual",
                                    f"Ventas Totales: COP {total:,.2f}\nImpuesto (Ventas Totales * 7 / 1000): COP {impuesto:,.2f}", parent=tabla_ventas)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=tabla_ventas)

        tk.Button(tabla_ventas, text="Calcular Impuesto", command=calcular_impuesto,
                  bg=self.BOTON4, fg="white", font=("Segoe UI", 15, "bold")).place(x=600, y=550)

    def ejecutar(self):
        self.ventana.mainloop()
