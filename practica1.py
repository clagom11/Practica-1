"""Práctica 1: PARTE OBLIGATORIA"""
"""Claudia Gómez Alonso"""
from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array, Manager
from time import sleep
from random import random, randint


N = 5 #número de productos que se producirán en cada proceso
NPROD = 4 #número de productores (procesos) que hay




def delay(factor = 3):
    sleep(random()/factor)

def add_data(storage, pid, data, mutex):
    mutex.acquire()
    try:
        storage[pid] = data
        #proceso[index.value] = pid #así en la misma posición que su dato, podemos ver qué proceso lo añadió.
        delay(6)
    finally:
        mutex.release()
"""Hacemos esta función auxiliar para que, una vez haya terminado el proceso (al salir del bucle for de
producer), se añada un -1 que lo indique y no impida que se continúen añadiendo elementos de otros
productores a la lista del proceso merge hasta que todos los productores hayan finalizado la producción 
(todos hayan producido -1)"""        
def add_menos_uno(storage, pid, mutex):
    mutex.acquire()
    try:
        storage[pid] = -1
        #proceso[index.value] = pid 
        delay(6)
    finally:
        mutex.release()



def producer(storage, empty, non_empty, mutex):
    producto = 0
    for v in range(N):
        #print (f"producer {current_process().name} produciendo")
        delay(6)
        num = randint(1,5)
        producto+=num
        empty.acquire()
        add_data(storage, int(current_process().name.split('_')[1]),
                 producto, mutex)
        non_empty.release()
        print (f"producer {current_process().name} almacenado {producto}" + '\n')
    empty.acquire()
    add_menos_uno(storage, int(current_process().name.split('_')[1]), mutex) #se llama a add_menos_uno, porque se ha acabado el proceso.
    non_empty.release()


def merge(storage, empty, non_empty, mutex, lista):
    
    for i in range(NPROD): #necesitamos que todos los procesos hayan producido, para poder comparar los productos.
        non_empty[i].acquire()
    
    
    minimo = max(storage)#número para inicializar y que siempre haya un elemento en storage que sea más pequeño y pase a ser el mínimo, sin ser -1, por las condiciones de después.

    while minimo != -1: #esto solo ocurrirá cuando todos los elementos de storage sean -1.
        pos = 0
        for j in range(len(storage)): #hallamos el mínimo (teniendo en cuenta que este no puede ser -1)
            print("storage: (",storage[j],", ", j, ")") 
            if (storage[j] >= 0) and (storage[j] <= minimo):
                minimo = storage[j] 
                pos = j #pos será en realidad el proceso al que pertenece el producto consumido.
        
        #index.value = pos #para guardar el elemento que añadamos (más adelante, en add_data) en la posición que ha quedado vacía.
        #p = proceso[pos] #para averiguar a qué proceso pertenece 
        print("Elemento añadido: ", minimo ,", perteneciente al proceso: " , pos , '\n') 
        storage[pos] = -2 #se ha consumido el elemento mínimo y se queda vacío 
        lista.append((minimo,pos))
        print("Lista con los productos del merge: ", lista)
        
        empty[pos].release()
        delay()
        non_empty[pos].acquire() #tenemos que esperar a que el proceso p obtenga un nuevo producto.
        minimo = max(storage) #actualizamos el máximo con los nuevos datos en storage.
    
def main():
    storage = Array('i', NPROD)
    index = Value('i', 0)
    lista = [] #esta será la lista en la que iremos guardando los elementos en orden creciente en el proceso merge.
    
    for i in range(NPROD):
        storage[i] = -2
    print ("almacen inicial", storage[:], "indice", index.value)

    non_empty = []
    empty = []
    mutex = Lock()
    
    for j in range(NPROD): #añadimos los semáforos para cada proceso en listas
        non_empty.append(Semaphore(0))
        empty.append(BoundedSemaphore(1)) #solo hay un producto cada vez.

    prodlst = [ Process(target=producer,
                        name=f'prod_{i}',
                        args=(storage, empty[i], non_empty[i], mutex))
                for i in range(NPROD) ]

    m = Process(target=merge,
                      args=(storage, empty, non_empty, mutex, lista))
               

    for p in prodlst:
        p.start()
    m.start()

    for p in prodlst:
        p.join()
    m.join


if __name__ == '__main__':
    main()
    
