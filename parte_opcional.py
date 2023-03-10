"""Práctica 1: PARTE OPCIONAL"""
"""Claudia Gómez Alonso"""

from multiprocessing import Process, Manager
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array
from time import sleep
from random import random, randint


N = 8
NPROD = 6
K = 4



def delay(factor = 3):
    sleep(random()/factor)

def add_data(storage, pid, data, mutex):
    mutex.acquire()
    try:
        indice = pid * K #para añadir los productos en la franja del storage correspondiente al proceso en el que estamos.
        cont = 0
        
        while storage[cont + indice] != -2:
            cont += 1
        storage[cont + indice] = data
        cont = 0
        
        delay(6)

    finally:
        mutex.release()
        
def add_menos_uno(storage,pid, mutex):
    mutex.acquire()
    try:
        indice = pid * K 
        cont = 0
        
        while storage[cont + indice] != -2:
            cont += 1
        storage[cont + indice] = -1 #colocamos el -1 en la posición correspondiente, cuando llegue al principio de cada franja, todo lo demás serán -2 y ya no habrá más productos de este proceso.
        cont = 0 
        delay(6)

    finally:
        mutex.release()



def producer(storage, empty, non_empty, mutex):
    producto = 0
    for v in range(N):
        delay(6)
        empty.acquire()
        pid =int(current_process().name.split('_')[1])
        num = randint(1,5)
        producto+=num
        

        add_data(storage, int(current_process().name.split('_')[1]),
                 producto, mutex)
        non_empty.release()
        print (f"producer {current_process().name} almacenado {producto}" + '\n')
    empty.acquire()
    add_menos_uno(storage, int(current_process().name.split('_')[1]), mutex)
    non_empty.release()


def merge(storage, empty, non_empty, mutex, lista):
    print("almacen:", storage)
    for i in range(NPROD):
        non_empty[i].acquire()
    
    
    minimo = max(storage)#así podremos encontrar otro que sea menor que él, a no ser que todos los demás sean -1.
    print("Mínimo: ", minimo)
    while minimo != -1:
        pos = 0
        for j in range(0,len(storage),K): #siempre nos fijamos en el primero que ha producido cada productor, por eso vamos de K en K.
            #hallamos el mínimo
 
            if (storage[j] >= 0) and (storage[j] <= minimo): 
                minimo = storage[j]
                pos = j
        
        productor = pos // K #para averiguar a que proceso pertenece el elemento añadido.
        print("Elemento añadido: ", minimo ,", perteneciente al proceso: " , productor , '\n') 
        
        lista.append((minimo,productor)) #añadimos el mínimo a la lista 
        print("Lista de elementos del merge: ", lista)
        
        #y ahora procedemos a consumirlo de storage, para lo que hacemos lo siguiente:
        for k in range(pos, pos + K): #movemos todos los elementos del buffer a la izquierda y añadimos un -2 al final.
            
            if k == pos + K -1:  #cuando nos encontramos en el último caso, tenemos que añadir en esa posición un -2.
                storage[k] = -2
            else:
                storage[k] = storage[k+1]
                
        #for j in range(len(storage)):
            #print("storage: (",storage[j],", ", j, ")")  #para ver cómo se nos queda el storage después de consumir el elemento correspondiente.
                


        minimo = max(storage)
        
        empty[productor].release()
        delay()
        non_empty[productor].acquire() #tenemos que esperar a q el proceso p obtenga un nuevo producto.
    
def main():
    storage = Array('i', NPROD * K)
    #proceso = Array('i', NPROD)
    #buffer = Array('i', K) #buffer de tamaño k para cada uno de los productores.
    #index = Value('i', 0)
    lista = []
    
    for i in range(NPROD * K):
        storage[i] = -2
    print ("almacen inicial", storage[:])

    non_empty = []
    empty = []
    mutex = Lock()
    
    for j in range(NPROD):
        non_empty.append(Semaphore(0))
        empty.append(BoundedSemaphore(K)) #puede haber más de un producto cada vez.

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




