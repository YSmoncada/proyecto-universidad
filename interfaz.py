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

        btn_frame = tk.Frame(self.ventana, bg=self.FONDO)
        btn_frame.pack(pady=10)

        botones = [
            ("Agregar a Inventario", self._ventana_inventario, self.BOTON1),
            ("Ver Inventario", self._ver_inventario, self.BOTON3),
            ("Agregar Ventas y Cálculo de Impuesto", self._ventana_ventas, self.BOTON2),
            ("Historial de Ventas", self._ver_ventas, self.BOTON4),
        ]

        for texto, accion, color in botones:
            tk.Button(btn_frame, text=texto, command=accion, bg=color, fg="white",
                      font=("Segoe UI", 12, "bold"), width=40, height=2).pack(pady=10)

    def _ventana_inventario(self):
        inv_win = tk.Toplevel()
        inv_win.title("Agregar Artículos al Inventario")
        inv_win.geometry("520x450")
        inv_win.configure(bg=self.FONDO)

        tk.Label(inv_win, text="Registrar Producto", font=("Segoe UI", 14, "bold"),
                 bg=self.FONDO, fg=self.TEXTO).pack(pady=10)

        campos = {}
        etiquetas = ["Nombre", "Código", "Vencimiento", "Precio", "Cantidad", "Medida"]
        for i, texto in enumerate(etiquetas):
            tk.Label(inv_win, text=texto, bg=self.FONDO, fg=self.TEXTO,
                     font=("Segoe UI", 10)).place(x=30, y=50 + i*40)
            entry = tk.Entry(inv_win, width=30, font=("Segoe UI", 10), bg=self.ENTRADA_BG)
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
        unidad_var = tk.StringVar(inv_win)
        unidad_var.set(unidades[0])

        tk.Label(inv_win, text="Unidad de Medida", bg=self.FONDO, fg=self.TEXTO,
                 font=("Segoe UI", 10)).place(x=30, y=50 + len(etiquetas)*40)
        unidad_menu = tk.OptionMenu(inv_win, unidad_var, *unidades)
        unidad_menu.place(x=160, y=50 + len(etiquetas)*40)

        def guardar():
            try:
                nombre = campos["nombre"].get().strip().title()
                codigo = campos["código"].get().strip()
                vencimiento_str = campos["vencimiento"].get().strip()

                precio_str = campos["precio"].get().strip().replace(",", ".")
                cantidad_str = campos["cantidad"].get().strip()
                medida = campos["medida"].get().strip()
                unidad = unidad_var.get()

                if not nombre or not codigo or not vencimiento_str or not precio_str or not cantidad_str or not medida:
                    messagebox.showerror("Error", "Todos los campos deben estar completos.")
                    return

                try:
                    vencimiento = datetime.strptime(vencimiento_str, "%d-%m-%Y").date()
                except ValueError:
                    messagebox.showerror("Error", "La fecha de vencimiento debe estar en formato dd-mm-aaaa.")
                    return

                try:
                    precio = float(precio_str)
                except ValueError:
                    messagebox.showerror("Error", "El precio debe ser un número válido (usa punto o coma como separador decimal).")
                    return

                try:
                    cantidad = int(cantidad_str)
                except ValueError:
                    messagebox.showerror("Error", "La cantidad debe ser un número entero.")
                    campos["precio"].delete(0, tk.END)
                    campos["precio"].focus_set()
                    return

                agregar_producto(nombre, codigo, vencimiento, precio, cantidad, medida, unidad)
                messagebox.showinfo("Producto registrado correctamente",
                            "El producto ha sido registrado exitosamente.")
                for campo in campos.values():
                    campo.delete(0, tk.END)
                campos["nombre"].focus_set()

            except Exception as e:
                messagebox.showerror("Error inesperado", str(e))

        tk.Button(inv_win, text="Guardar", command=guardar, bg=self.BOTON1, fg="white",
                  font=("Segoe UI", 10, "bold")).place(x=200, y=350)

    def _ver_inventario(self):
        win = tk.Toplevel()
        win.title("Inventario")
        win.geometry("1600x860")
        win.configure(bg=self.FONDO)

        tk.Label(win, text="Inventario de Productos", font=("Segoe UI", 14, "bold"),
                 bg=self.FONDO, fg=self.TEXTO).pack(pady=10)

        columnas = ("Nombre", "Código", "Vencimiento / Días restantes", "Precio", "Cantidad", "Medida", "Unidad")
        tabla = ttk.Treeview(win, columns=columnas, show="headings", height=30)
        for col in columnas:
            tabla.heading(col, text=col)
            tabla.column(col, anchor="center")

        scrollbar = ttk.Scrollbar(win, orient="vertical", command=tabla.yview)
        tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tabla.pack(fill="both", expand=True)

        def actualizar_tabla():
            tabla.delete(*tabla.get_children())
            for producto in obtener_productos():
                try:
                    vencimiento_date = producto.vencimiento
                    hoy = date.today()
                    dias_restantes = (vencimiento_date - hoy).days

                    if dias_restantes < 0:
                        vencimiento_str = f"{vencimiento_date.strftime('%d-%m-%Y')} (¡VENCIDO!)"
                    else:
                        vencimiento_str = f"{vencimiento_date.strftime('%d-%m-%Y')} ({dias_restantes} días restantes)"
                except Exception as e:
                    vencimiento_str = f"Error: {e}"

                tabla.insert('', 'end', values=(
                    producto.nombre, producto.codigo, vencimiento_str,
                    f"${producto.precio:.2f}", producto.cantidad, producto.medida, producto.unidad))

        def eliminar_producto_evento():
            try:
                seleccion = tabla.selection()
                if not seleccion:
                    messagebox.showwarning("Advertencia", "Por favor selecciona un producto para eliminar.", parent=win)
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

        tk.Button(win, text="Eliminar Producto", command=lambda: eliminar_producto_evento(), bg=self.BOTON1, fg="white",
                  font=("Segoe UI", 15, "bold")).place(x=600, y=550)

    def _ventana_ventas(self):
        ventas_win = tk.Toplevel()
        ventas_win.title("Registrar Ventas y Calcular Impuestos")
        ventas_win.geometry("420x300")
        ventas_win.configure(bg=self.FONDO)

        tk.Label(ventas_win, text="Registrar Venta", font=("Segoe UI", 14, "bold"),
                 bg=self.FONDO, fg=self.TEXTO).pack(pady=10)

        campos = {}
        etiquetas = ["Nombre", "Cantidad", "Medida"]
        for i, texto in enumerate(etiquetas):
            tk.Label(ventas_win, text=texto, bg=self.FONDO, fg=self.TEXTO,
                     font=("Segoe UI", 10)).place(x=30, y=50 + i*40)
            entry = tk.Entry(ventas_win, width=30, font=("Segoe UI", 10), bg=self.ENTRADA_BG)
            entry.place(x=120, y=50 + i*40)
            campos[texto.lower()] = entry

        unidades = ["Litros", "Mililitros", "Kilos", "Gramos"]
        unidad_var = tk.StringVar(ventas_win)
        unidad_var.set(unidades[0])

        tk.Label(ventas_win, text="Unidad de Medida", bg=self.FONDO, fg=self.TEXTO,
                 font=("Segoe UI", 10)).place(x=30, y=50 + len(etiquetas)*40)
        unidad_menu = tk.OptionMenu(ventas_win, unidad_var, *unidades)
        unidad_menu.place(x=160, y=50 + len(etiquetas)*40)

        def registrar_venta():
            try:
                nombre = campos["nombre"].get().strip()
                cantidad = int(campos["cantidad"].get().strip())
                medida = campos["medida"].get().strip()
                unidad = unidad_var.get().strip()

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

                vender_producto(nombre, cantidad, medida, unidad)
                messagebox.showinfo("Venta registrada con éxito",
                                     "La venta ha sido registrada exitosamente.")
                ventas_win.destroy()
                self._ver_ventas()

            except ValueError:
                messagebox.showerror("Error", "La cantidad debe ser un número entero.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        def calcular_impuesto():
            try:
                total = obtener_ventas_totales()
                impuesto = calcular_impuesto_anual(total)
                messagebox.showinfo("Impuesto Anual",
                                    f"Ventas Totales: ${total:.2f}\nImpuesto (Ventas Totales * 7 / 1000): ${impuesto:.2f}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(ventas_win, text="Registrar Venta", command=registrar_venta,
                  bg=self.BOTON2, fg="white", font=("Segoe UI", 10, "bold")).place(x=40, y=200)
        tk.Button(ventas_win, text="Calcular Impuesto", command=calcular_impuesto,
                  bg=self.BOTON4, fg="white", font=("Segoe UI", 10, "bold")).place(x=200, y=200)

    def _ver_ventas(self):
        win = tk.Toplevel()
        win.title("Historial de Ventas")
        win.geometry("1600x860")
        win.configure(bg=self.FONDO)

        tk.Label(win, text="Historial de Ventas", font=("Segoe UI", 14, "bold"),
                 bg=self.FONDO, fg=self.TEXTO).pack(pady=10)

        columnas = ("Producto", "Cantidad", "Medida", "Unidad", "Fecha")
        tabla = ttk.Treeview(win, columns=columnas, show="headings", height=30)
        for col in columnas:
            tabla.heading(col, text=col)
            tabla.column(col, anchor="center")

        scrollbar = ttk.Scrollbar(win, orient="vertical", command=tabla.yview)
        tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tabla.pack(fill="both", expand=True)

        def actualizar_tabla():
            tabla.delete(*tabla.get_children())
            for venta in obtener_ventas():
                tabla.insert('', 'end', values=(
                    venta["nombre"], venta["cantidad"], venta["medida"], venta["unidad"],
                    venta["fecha"]))

        actualizar_tabla()

    def ejecutar(self):
        self.ventana.mainloop()


