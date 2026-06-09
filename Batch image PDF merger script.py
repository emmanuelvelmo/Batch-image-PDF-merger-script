import pathlib # Manejo de rutas de archivos y directorios
import cv2 # Lectura de imágenes y redimensionamiento
import fitz # Creación de documentos PDF y manipulación de páginas

# VARIABLES GLOBALES
extensiones_lista = ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'webp'] # Lista de formatos de imagen soportados
tamano_pagina_carta = (612, 792) # Tamaño carta en puntos: 8.5 x 11 pulgadas

# FUNCIONES
# Calcula dimensiones para ajustar imagen a página manteniendo relación de aspecto
def calcular_ajuste(ancho_img, alto_img, ancho_pag, alto_pag):
    # Calcular relación de aspecto de la imagen
    relacion_img = ancho_img / alto_img
    
    # Calcular relación de aspecto de la página
    relacion_pag = ancho_pag / alto_pag
    
    # Determinar si ajustar por ancho o por alto
    if relacion_img > relacion_pag:
        # Imagen más ancha relativa: ajustar por ancho
        ancho_ajustado = ancho_pag
        alto_ajustado = ancho_pag / relacion_img
    else:
        # Imagen más alta relativa: ajustar por alto
        alto_ajustado = alto_pag
        ancho_ajustado = alto_pag * relacion_img
    
    return ancho_ajustado, alto_ajustado

# Convierte imagen de OpenCV a bytes PNG (sin usar PIL)
def imagen_a_bytes_png(imagen_rgb):
    # Codificar imagen como PNG en buffer de memoria
    exito_val, buffer_val = cv2.imencode('.png', imagen_rgb)
    
    # Convertir buffer a bytes
    return buffer_val.tobytes()

# Procesa y agrega una imagen al documento PDF en nueva página
def agregar_imagen_a_pdf(documento_pdf, ruta_imagen):
    # Cargar imagen usando OpenCV
    imagen_val = cv2.imread(str(ruta_imagen))
    
    # Convertir de BGR (OpenCV) a RGB
    imagen_rgb = cv2.cvtColor(imagen_val, cv2.COLOR_BGR2RGB)
    
    # Convertir imagen a bytes PNG
    bytes_imagen = imagen_a_bytes_png(imagen_rgb)
    
    # Obtener dimensiones originales de la imagen
    alto_img, ancho_img = imagen_rgb.shape[:2]
    
    # Calcular dimensiones ajustadas para página carta
    ancho_ajustado, alto_ajustado = calcular_ajuste(ancho_img, alto_img, tamano_pagina_carta[0], tamano_pagina_carta[1])
    
    # Calcular posición para centrar imagen en la página
    pos_x = (tamano_pagina_carta[0] - ancho_ajustado) / 2
    pos_y = (tamano_pagina_carta[1] - alto_ajustado) / 2
    
    # Crear nueva página en el documento
    pagina_val = documento_pdf.new_page(width = tamano_pagina_carta[0], height = tamano_pagina_carta[1])
    
    # Insertar imagen en la página usando los bytes
    pagina_val.insert_image(rect = (pos_x, pos_y, pos_x + ancho_ajustado, pos_y + alto_ajustado), stream = bytes_imagen)

# Procesa todas las imágenes del directorio y genera PDF
def procesar_directorio_imagenes(directorio_entrada_str, nombre_pdf_salida):
    # Convertir string a objeto Path
    directorio_entrada = pathlib.Path(directorio_entrada_str)
    
    # Crear nuevo documento PDF
    documento_pdf = fitz.open()
    
    # Lista para almacenar rutas de imágenes encontradas
    lista_imagenes = []
    
    # Buscar todas las imágenes en el directorio recursivamente
    for extension_val in extensiones_lista:
        for archivo_iter in directorio_entrada.rglob(f'*.{extension_val}'):
            if archivo_iter.is_file():
                # Agregar ruta a la lista
                lista_imagenes.append(archivo_iter)
    
    # Ordenar lista de imágenes por nombre de archivo
    lista_imagenes.sort(key = lambda x: str(x.name))
    
    cont_imagenes_cargadas = 0 # Contador de imágenes procesadas
    
    # Mostrar separador visual
    print("-" * 36)
    
    # Procesar cada imagen en orden
    for archivo_iter in lista_imagenes:
        try:
            # Mostrar archivo procesado
            print(str(archivo_iter))
            
            # Agregar imagen al PDF
            agregar_imagen_a_pdf(documento_pdf, archivo_iter)
            
            cont_imagenes_cargadas += 1
        
        except Exception as e:
            # Mostrar error pero continuar con siguiente imagen
            print(f"Error processing {archivo_iter.name}: {str(e)}")
    
    # Mostrar mensaje si no se procesaron imágenes
    if cont_imagenes_cargadas == 0:
        print("No images processed")
    else:
        # Guardar documento PDF
        ruta_pdf_salida = pathlib.Path(nombre_pdf_salida)
        
        # Agregar extensión .pdf si no tiene
        if ruta_pdf_salida.suffix.lower() != '.pdf':
            ruta_pdf_salida = ruta_pdf_salida.with_suffix('.pdf')
        
        # Guardar PDF
        documento_pdf.save(str(ruta_pdf_salida))
        
        # Mostrar mensaje de procesamiento
        print(f"\n{ruta_pdf_salida.name} processed")
    
    # Cerrar documento PDF
    documento_pdf.close()
    
    # Mostrar separador final
    print("-" * 36 + "\n")

# PUNTO DE PARTIDA
# Bucle principal del programa
while True:
    # Solicitar directorio de entrada
    while True:
        directorio_entrada_val = input("Enter directory: ").strip('"\'')
        
        if not pathlib.Path(directorio_entrada_val).exists():
            print("Wrong directory\n")
        else:
            break
    
    # Solicitar nombre del archivo PDF de salida
    nombre_pdf_val = input("Enter output PDF name: ").strip('"\'')
    
    # Procesar directorio de imágenes y generar PDF
    procesar_directorio_imagenes(directorio_entrada_val, nombre_pdf_val)