import os
import pandas as pd

# === CONFIGURACIÓN ===
input_folder = r"C:\ruta\a\tu\carpeta"   # 🔹 Cambia por tu carpeta con archivos .txt
output_file = r"C:\ruta\a\tu\salida\frecuencias.xlsx"  # 🔹 Excel final

# === PROCESAMIENTO ===
writer = pd.ExcelWriter(output_file, engine='openpyxl')

for file_name in os.listdir(input_folder):
    if file_name.lower().endswith(".txt"):
        file_path = os.path.join(input_folder, file_name)
        print(f"Procesando: {file_name}")

        # Leer el archivo .txt
        # Usa 'python engine' y separador flexible con regex
        df = pd.read_csv(
            file_path,
            sep=r'\s{2,}',              # separa por 2 o más espacios (mantiene espacios simples dentro del dato)
            engine='python',
            encoding='utf-8',
        )

        # Limpieza opcional: eliminar filas vacías
        df.dropna(how='all', inplace=True)

        # Renombrar hoja (máx 31 caracteres en Excel)
        sheet_name = os.path.splitext(file_name)[0][:31]

        # Escribir al Excel
        df.to_excel(writer, sheet_name=sheet_name, index=False)

writer.close()
print(f"\n✅ Archivo Excel generado en: {output_file}")
