# Drive de TONOBUCK (Antonio)
from google.colab import drive
drive.mount('/content/drive')

from PIL import Image
from random import choice
import time
import os
TAM_DEFAULT = (32, 32)
FAC = 5

# Crea la base de la estructura de datos para guardar las entradas {color : caminoAImagen}
def crearData():
  return [None]*(1 + 255//FAC)

data = crearData()

# Saca el color promedio de una imagen
def colorPromedio(img):
  px = img.load()
  r, g, b = 0, 0, 0
  for x in range(img.width):
    for y in range(img.height):
      color = px[x,y]
      r += color[0]
      g += color[1]
      b += color[2]
  a = img.width*img.height
  del px
  return r//a, g//a, b//a

# Meta la entrada {color, caminoAImagen} en la estructura de datos. Si faltan componentes a la estructura, se agregan.
def meterData(data, color, img):
  r, g, b = color[0]//FAC, color[1]//FAC, color[2]//FAC
  if data[r] == None:
    data[r] = crear_data()
    data[r][g] = crear_data()
  elif data[r][g] == None:
    data[r][g] = crear_data()
  data[r][g][b] = img

# Carga una imagen y le aplica procesamiento.
def procesar(nombre):
  with Image.open(nombre).convert("RGB") as img:
    img = img.resize(TAM_DEFAULT)
    promedio = colorPromedio(img)
    meterData(data, promedio, nombre)
    del img

# Crea una imagen vacía
def crearImagenVacia(imagenOriginal):
  x, y = imagenOriginal.size
  imagenVacia = Image.new("RGB",(x*TAM_DEFAULT[0],y*TAM_DEFAULT[1]))
  return imagenVacia

# Reeplaza los pixeles del collage en la posición respectiva.
def reemplazarPixeles(posXInicio,posYInicio,vacia,color):
  with Image.open(determinarImagen(data, color)) as img:
    img.resize(TAM_DEFAULT)
    vacia.paste(img, (posXInicio,posYInicio))
    del img

# Maneja todo lo que es la creación del collage
def recorrerPixeles(imagenOriginal):
  # Redimensiomaniento.
  if imagenOriginal.width > imagenOriginal.height:
    scale = imagenOriginal.height/imagenOriginal.width
    imagenOriginal = imagenOriginal.resize((256, int(scale*256)))
  else:
    scale = imagenOriginal.width/imagenOriginal.height
    imagenOriginal = imagenOriginal.resize((int(scale*256), 256))
  img = imagenOriginal.load()
  vacia = crearImagenVacia(imagenOriginal)
  mult = imagenOriginal.width*imagenOriginal.height
  # Recorrimiento pixel por pixel
  for i in range(imagenOriginal.width):
    for j in range(imagenOriginal.height):
      reemplazarPixeles(i*TAM_DEFAULT[0],j*TAM_DEFAULT[1],vacia,img[i,j])
  return vacia

# Eliga el color más cercano.
def elegirCercano(lista, pos):
  final = []
  l = len(lista)
  for i in range(1, l):
    if i + pos < l and lista[i + pos] != None: final.append(lista[i + pos])
    if pos - i >= 0 and lista[pos - i] != None: final.append(lista[pos - i])
    if final != []: break
  return choice(final)

def determinarImagen(data, color):
  r, g, b = color[0]//FAC, color[1]//FAC, color[2]//FAC
  work = data
  if work[r] == None:
    work = elegirCercano(work, r)
  else:
    work = work[r]
  if work[g] == None:
    work = elegirCercano(work, g)
  else:
    work = work[g]
  if work[b] == None:
    work = elegirCercano(work, b)
  else:
    work = work[b]
  return work

imgsP = "/content/drive/MyDrive/imagenesPrueba/watercolor"
imagenesNombres = os.listdir(imgsP) #variable con la carpeta

# Fase que consiste en procesamiento de las imágenes iniciales.
print("Iniciando fase 1...")

MAX_RUN = 2000

inicio = time.time()
for i in range(min(MAX_RUN, len(imagenesNombres))):
  procesar(imgsP+"/"+imagenesNombres[i])

print("Procesamiento finalizando!!!")
print("Duracion de fase 1: ", time.time()-inicio)

#------------------------------

imagenACambiar = "/content/drive/MyDrive/marisco.jpg"

# Fase que consiste en la creación del collage.
print("Iniciando fase 2...")
inicio = time.time()
imagenACambiar = Image.open(imagenACambiar).convert("RGB")
nueva = recorrerPixeles(imagenACambiar)
nueva.save("NUEVA.png")

print("Duracion de fase 2: ", time.time()-inicio)
