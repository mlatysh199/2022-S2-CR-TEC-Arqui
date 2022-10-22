# Drive de PYPROGRAMMER (Max)

from google.colab import drive
drive.mount('/content/drive')
from multiprocessing import Pool, Manager
from PIL import Image
from random import choice
import time
import os
import numpy as np
TAM_DEFAULT = (16, 16)
FAC = 5
FACTOR = 1 + 255//FAC

# Crea la estructura de datos para contener todo lo que es los colores e imágenes asociadas.
def crearData(manager):
  return manager.list([manager.list([manager.list([None for i in range(FACTOR)]) for j in range(FACTOR)]) for k in range(FACTOR)])

# Crea una estructura para saber cuales colores han sido encontrados.
def crearSubdata(manager):
  return manager.list([False]*FACTOR)

# Crea otra estructura complementaria a la función anterior.
def crearSubsubdata(manager):
  return manager.list([manager.list([False]*FACTOR) for i in range(FACTOR)])

# Saca el color promedio de una imagen.
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

# Meta la entrada {color : caminoAImagen} en la estructura y cambia registros.
def meterData(data, subdata, subsubdata, color, img):
  r, g, b = color[0]//FAC, color[1]//FAC, color[2]//FAC
  subdata[r] = True
  subsubdata[r][g] = True
  data[r][g][b] = img

# Dado una imagen, lo procesa.
def procesar(data, subdata, subsubdata ,nombre):
  with Image.open(nombre).convert("RGB") as img:
    img = img.resize(TAM_DEFAULT)
    promedio = colorPromedio(img)
    meterData(data, subdata, subsubdata, promedio, nombre)
    del img

# Crea un plano vació para el collage.
def crearImagenVacia(imagenOriginal):
  x, y = imagenOriginal.size
  imagenVacia = Image.new("RGB",(x*TAM_DEFAULT[0],y*TAM_DEFAULT[1]))
  return imagenVacia

# Pega una mini imagen sobre el collage.
# - Aquí no se puede utilizar Image.paste() debido a que se tiene que utilizar
# - una estructura de memoria compartida que no es compatible con la clase
# - Image.
def pegar(nuevaData, img, posx, posy, mx, my):
  try:
    pos = posx*TAM_DEFAULT[0]+posy*TAM_DEFAULT[1]*mx
    #pos *= TAM_DEFAULT[0]*TAM_DEFAULT[1]
    for i in range(TAM_DEFAULT[1]):
      for j in range(TAM_DEFAULT[0]):
        nuevaData[pos + i*mx + j] = img[j,i]
  except Exception as e:
    pass

# Reemplaza determina, carga, y pega la imagen respectiva al pixel en cuestión en el collage.
def reemplazarPixeles(ent):
  nuevaData, posx, posy,color, data, subdata, subsubdata, mx, my = ent
  with Image.open(determinarImagen(data, subdata, subsubdata, color)).convert("RGB") as img:
    img = img.resize(TAM_DEFAULT).load()
    # Más eficiente si se hace con numpy, pero no se puede guardar bien para multiprocessing.
    #vacia[posYInicio:posYInicio+TAM_DEFAULT[1],posXInicio:posXInicio+TAM_DEFAULT[0]] = np.array(img)
    pegar(nuevaData, img, posx, posy, mx, my)
    del img

# Elige el color más cercano a una entrada.
def elegirCercano(pos, criterio):
  final = []
  for i in range(0, FACTOR):
    if i + pos < FACTOR and criterio[i + pos]: final.append(i + pos)
    if pos - i >= 0 and criterio[pos - i]: final.append(pos - i)
    if final != []: break
  return choice(final) # Permite tener variedad en algunas ocasiones

# Determina el camino a la imagen que más parezca al pixel.
def determinarImagen(data, subdata, subsubdata, color):
  r, g, b = color[0]//FAC, color[1]//FAC, color[2]//FAC
  p1 = elegirCercano(r, subdata)
  p2 = elegirCercano(g, subsubdata[p1])
  p3 = elegirCercano(b, data[p1][p2])
  return data[p1][p2][p3]

# Procesa un medio de las imagenes.
def procesamientoParte(rango):
  for i in range (rango[0],rango[1]):
      procesar(rango[2], rango[3], rango[4],rango[5]+"/"+rango[6][i])

# Para multiprocessing
if __name__ == "__main__":
  inicio = time.time()
  
  # Fase uno consiste en crear la estructura de datos principial y después meterle todas las imágenes.
  print("Iniciando fase 1...")
  manager = Manager()
  
  data = crearData(manager)
  subdata = crearSubdata(manager)
  subsubdata = crearSubsubdata(manager)
  imgsP = "/content/drive/MyDrive/test"
  #imgs_p = "/content/drive/MyDrive/imagenesPrueba/watercolor"
  imagenesNombres = os.listdir(imgsP) #variable con la carpeta
  MAX_RUN = 2000
  
  # Multiprocessing con dos cores debido a google colab.
  with Pool(2) as p:
    p.map(procesamientoParte, [(min(MAX_RUN,len(imagenesNombres))*i//2,min(MAX_RUN,len(imagenesNombres))//2*(i+1), data, subdata, subsubdata, imgsP, imagenesNombres) for i in range(2)])

  print("Procesamiento finalizando!!!")
  print("Duracion de fase 1: ", time.time() - inicio)

  #------------------------------

  #imagenACambiar = "/content/drive/MyDrive/panas.jpeg"
  imagenACambiar = "/content/drive/MyDrive/icpc1.jpg"

  
  # La fase dos consiste en empezar el proceso de reemplazo para crear el collage en sí.
  print("Iniciando fase 2...")
  inicio = time.time()
  imagenOriginal = Image.open(imagenACambiar).convert("RGB")
  #nueva = recorrerPixeles(imagenACambiar, data, subdata, subsubdata)
  
  # Si dejamos la imagen con el mismo tamaño de antes, no se va poder procesar.
  if imagenOriginal.width > imagenOriginal.height:
    scale = imagenOriginal.height/imagenOriginal.width
    imagenOriginal = imagenOriginal.resize((100, int(scale*100)))
  else:
    scale = imagenOriginal.width/imagenOriginal.height
    imagenOriginal = imagenOriginal.resize((int(scale*100), 100))
    
  # Cargamos la imagen y creamos en plano vacío.
  img = imagenOriginal.load()
  nueva = crearImagenVacia(imagenOriginal)
  nueva.readonly = False
  nuevaData = None
  try:
    # CLAVE: tenemos que guardar la imagen en sí dentro de la memoria compartida.
    # - Sino, el multiprocesamiento provocará la formación de copias separadas, y nada se terminará guardando.
    # - manager.list() Nos permite convertir una lista en una lista de memoria compartida; la lista resultante es muy lenta.
    nuevaData = manager.list(list(nueva.getdata())) # Código bastante eficiente, pero no logré encontrar otra manera de guardar una imagen en recursos compartidos.
  except Exception as e:
    raise(Exception())
  
  # multiprocessing a todos los pixeles de la imagen original redimensionada (max 100x100).
  with Pool(2) as p:
    p.map(reemplazarPixeles, [(nuevaData, i%imagenOriginal.width, i//imagenOriginal.width, img[(i%imagenOriginal.width),(i//imagenOriginal.width)], data, subdata, subsubdata, imagenOriginal.width*TAM_DEFAULT[0], imagenOriginal.height*TAM_DEFAULT[1]) for i in range(imagenOriginal.height*imagenOriginal.width)])
  # Después utilizamos la lista para guardar la imagen en sí.
  nueva.putdata(nuevaData) # Código bastante ineficiente...
  # Guardamos el resultado.
  nueva.save("NUEVA.png")

  print("Duracion de fase 2: ", time.time()-inicio)
