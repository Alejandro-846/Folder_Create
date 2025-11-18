from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog
import zipfile
import os

# Variable global para guardar la ruta seleccionada
ruta_destino = Path.cwd()

def seleccionar_carpeta():
    """Permite al usuario elegir una carpeta destino."""
    global ruta_destino
    ruta_elegida = filedialog.askdirectory(title="Selecciona la carpeta destino")
    if ruta_elegida:
        ruta_destino = Path(ruta_elegida)
        lbl_ruta.config(text=f"Destino: {ruta_destino}")
    else:
        messagebox.showinfo("Aviso", "No seleccionaste ninguna carpeta. Se usará la carpeta actual.")

def comprimir_carpetas_ct():
    """Selecciona una carpeta CT y comprime cada componente INV-* dentro de ella automáticamente."""
    try:
        # Seleccionar carpeta CT
        carpeta_ct = filedialog.askdirectory(title="Selecciona la carpeta CT")
        if not carpeta_ct:
            return
        
        carpeta_ct_path = Path(carpeta_ct)
        
        # Buscar todas las carpetas INV-* dentro de CT
        inv_dirs = [d for d in carpeta_ct_path.iterdir() if d.is_dir() and d.name.startswith("INV-")]
        
        if not inv_dirs:
            messagebox.showwarning("Aviso", f"No se encontraron carpetas INV-* dentro de {carpeta_ct_path.name}")
            return
        
        def _add_empty_dir(zipf, arcdir: Path):
            info = zipfile.ZipInfo(str(arcdir).replace("\\", "/") + "/")
            zipf.writestr(info, b"")
        
        creados = []
        errores = []
        
        for inv_dir in inv_dirs:
            zip_name = f"{inv_dir.name}.zip"
            zip_path = carpeta_ct_path / zip_name
            
            # Evitar sobrescribir
            contador = 1
            while zip_path.exists():
                zip_path = carpeta_ct_path / f"{inv_dir.name}_{contador}.zip"
                contador += 1
            
            try:
                with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                    # Recorrer todo lo que está dentro de la carpeta INV
                    for root, dirs, files in os.walk(inv_dir):
                        root_path = Path(root)
                        # Añadir directorios vacíos
                        for d in dirs:
                            dir_path = root_path / d
                            arcdir = dir_path.relative_to(inv_dir.parent)
                            _add_empty_dir(zf, arcdir)
                        # Añadir archivos
                        for f in files:
                            file_path = root_path / f
                            arcname = file_path.relative_to(inv_dir.parent)
                            zf.write(file_path, arcname)
                
                creados.append(zip_path.name)
            except Exception as e:
                errores.append(f"{inv_dir.name}: {str(e)}")
        
        if creados:
            listado = "\n".join(creados)
            mensaje = f"Se comprimieron {len(creados)} componentes:\n{listado}"
            if errores:
                mensaje += f"\n\nErrores:\n" + "\n".join(errores)
            messagebox.showinfo("Éxito", mensaje)
        else:
            messagebox.showerror("Error", f"No se pudo comprimir ningún componente.\n\n" + "\n".join(errores))
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un problema:\n{e}")

def crear_carpetas():
    try:
        # Obtener los valores ingresados
        nombreCT = nombre_ct.get().strip()
        numero_name_inversor = num_inv.get().strip()
        nombreDivice = dispositivo.get()  # Valor de los radio buttons (PVPM o METREL)
        strings = entry_subcarpetas.get().strip()

        # Validaciones básicas
        if not nombreCT or not numero_name_inversor or not strings:
            messagebox.showerror("Error", "Por favor llena todos los campos.")
            return

        if not numero_name_inversor.isdigit() or not strings.isdigit():
            messagebox.showerror("Error", "Solo se permiten números en Inversor y Strings.")
            return

        numero_inv_int = int(numero_name_inversor)
        strings_int = int(strings)

        # Límite de inversores
        if numero_inv_int < 1 or numero_inv_int > 50:
            messagebox.showerror("Error", "El número de inversor debe estar entre 1 y 50.")
            return

        # Límite de strings
        if strings_int < 1 or strings_int > 100:  # Puedes cambiar el 100 por otro límite
            messagebox.showerror("Error", "La cantidad de strings debe estar entre 1 y 100.")
            return

    except ValueError:
        messagebox.showerror("Error", "Por favor ingresa solo números válidos.")
        return

    try:
        # Usar la carpeta seleccionada por el usuario
        ruta = ruta_destino

        for i in range(1, strings_int + 1):
            carpeta_ct = ruta / f"CT-{nombreCT}" / f"INV-{numero_name_inversor}-{nombreDivice}" / f"String-{i}"
            carpeta_ct.mkdir(parents=True, exist_ok=True)

        messagebox.showinfo(
            "Éxito",
            f"Se crearon {strings_int} carpetas dentro de:\n"
            f"{ruta}/{nombreCT}/INV-{numero_name_inversor}-{nombreDivice}"
        )
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un problema:\n{e}")

# --- Interfaz gráfica ---
ventana = tk.Tk()
ventana.title("Creador de Carpetas CT/INV")
ventana.geometry("460x420")
ventana.resizable(False, False)

# Botón para seleccionar carpeta
tk.Button(ventana, text="Seleccionar carpeta destino", command=seleccionar_carpeta).pack(pady=8)
lbl_ruta = tk.Label(ventana, text=f"Destino: {ruta_destino}", wraplength=400, justify="center")
lbl_ruta.pack()

# CT
tk.Label(ventana, text="Número del CT:").pack(pady=5)
nombre_ct = tk.Entry(ventana)
nombre_ct.pack()

# Dispositivo (PVPM / METREL)
tk.Label(ventana, text="Seleccione el tipo de dispositivo:").pack(pady=5)
dispositivo = tk.StringVar(value="PVPM")  # Valor por defecto
frame_dispo = tk.Frame(ventana)
frame_dispo.pack()
tk.Radiobutton(frame_dispo, text="PVPM", variable=dispositivo, value="PVPM").pack(side="left", padx=10)
tk.Radiobutton(frame_dispo, text="METREL", variable=dispositivo, value="METREL").pack(side="left", padx=10)

# Inversor
tk.Label(ventana, text="Número del Inversor (1–50):").pack(pady=5)
num_inv = tk.Entry(ventana)
num_inv.pack()

# Strings
tk.Label(ventana, text="Cantidad de Strings del INV (1–100):").pack(pady=5)
entry_subcarpetas = tk.Entry(ventana)
entry_subcarpetas.pack()

# Botón principal
tk.Button(ventana, text="Crear Carpetas", command=crear_carpetas, bg="#4CAF50", fg="white").pack(pady=15)
# Botón para comprimir carpetas CT
tk.Button(ventana, text="Comprimir Carpetas CT", command=comprimir_carpetas_ct, bg="#2196F3", fg="white").pack(pady=5)

ventana.mainloop()
