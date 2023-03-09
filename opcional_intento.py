#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 19:45:41 2023

@author: prpa
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 18:24:51 2023

@author: prpa
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 13:03:06 2023

@author: prpa
"""
"""
from multiprocessing import Process, Manager
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array
from time import sleep
from random import random, randint


N = 5
NPROD = 4
K = 3



def delay(factor = 3):
    sleep(random()/factor)

def add_data(storage,indice, pid, data, mutex):
    mutex.acquire()
    try:
        storage[pid][indice] = data
        print("elem",data)
        delay(6)
        print("almacen desde get data: ",storage)
        delay(6)

    finally:
        mutex.release()
        
def add_menos_uno(storage,pid, mutex):
    mutex.acquire()
    try:
        storage[pid][0] = -1 #cuando el proceso termina, añadimos un -1 al principio del buffer y es el que siempre se tendrá en cuenta y nos indica que el productor ha terminado de producir.
        delay(6)

    finally:
        mutex.release()



def producer(storage, empty, non_empty, mutex):
    producto = 0
    indice = 0
    for v in range(N):
        delay(6)
        empty.acquire()
        pid =int(current_process().name.split('_')[1])
        num = randint(1,5)
        producto+=num
        
        for i in range(len(storage[pid])): #para determinar siempre cuál es el valor de índice.
            if storage[pid][i] != -2:
                indice += 1 

        add_data(storage, indice, int(current_process().name.split('_')[1]),
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
    
    
    minimo = max(storage)[0] #es aquel que tiene el primer número de todos más alto que el de los demás productores
    #así podremos encontrar otro que sea menor que él, a no ser que todos los demás sean -1.
    print(minimo)
    while minimo != -1:
        proc = 0
        for j in range(len(storage)): #hallamos el mínimo y vamos contando los -1
            #print("storage: (",storage[j],", ", j, ")") 
            
            if (storage[j][0] >= 0) and (storage[j][0] <= minimo): #siempre nos fijamos en el primero que ha producido cada productor.
                minimo = storage[j][0]
                proc = j
        
        #index.value = pos
        print("Elemento añadido: ", minimo ,", perteneciente al proceso: " , j , '\n') 

        #movemos todos los productos añadidos al buffer por ese productor una unidad a la derecha, si es que hay alguno.
        #y añadimos un -2 al final, que queda vacío.
        for j in range(len(storage[proc])):
            if j == K-1:
                storage[proc][j] == -2
            else:
                storage[proc][j] = storage[proc][j+1]
        
        lista.append((minimo,proc))
        
            

        print(lista)
        minimo = max(storage)
        
        empty[proc].release()
        delay()
        non_empty[proc].acquire() #tenemos que esperar a q el proceso p obtenga un nuevo producto.
    
def main():
    storage = Manager().list()
    #proceso = Array('i', NPROD)
    #buffer = Array('i', K) #buffer de tamaño k para cada uno de los productores.
    #index = Value('i', 0)
    lista = []
    
    for i in range(NPROD):
        storage.append([-2] * K)
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
"""
    
    
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 19:45:41 2023

@author: prpa
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 18:24:51 2023

@author: prpa
"""

from multiprocessing import Process, Manager
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array
from time import sleep
from random import random, randint


N = 5
NPROD = 4
K = 3



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
        storage[pid * K] = -1 #cuando el proceso termina, añadimos un -1 al principio del buffer y es el que siempre se tendrá en cuenta y nos indica que el productor ha terminado de producir.
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
    print(minimo)
    while minimo != -1:
        pos = 0
        for j in range(len(storage)):
            print("storage: (",storage[j],", ", j, ")") 
        for j in range(0,len(storage),K): #siempre nos fijamos en el primero que ha producido cada productor, por eso vamos de K en K.
            #hallamos el mínimo
 
            if (storage[j] >= 0) and (storage[j] <= minimo): 
                minimo = storage[j]
                pos = j
        
        productor = pos // 3 #para averiguar a que proceso pertenece el elemento añadido.
        print("Elemento añadido: ", minimo ,", perteneciente al proceso: " , productor , '\n') 
        
        
        lista.append((minimo,productor)) #añadimos el mínimo a la lista 
        
        mutex.acquire() #para que no haya productos nuevos mientras estamos cambiando de posición los sitios.
        
        #y ahora procedemos a consumirlo de storage, para lo que hacemos lo siguiente:
        for k in range(pos, pos + K): #movemos todos los elementos del buffer a la izquierda y añadimos un -2 al final.
            
            if k == pos + K -1:  #cuando nos encontramos en el último caso, tenemos que añadir en esa posición un -2.
                storage[k] = -2
            else:
                storage[k] = storage[k+1]
                
        mutex.release()
        print(lista)
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

"""LO QUE VEO QUE PASA ES QUE DESPUÉS DE QUE LOS PROCESOS TENGAN -1, SE SIGUE PRODUCIENDO Y NO SÉ POR QUÉ
Además, debe ser que se sobreescriben algunos elementos o algo, porque se produce menos de lo q se debe
Puede ser que ocurra esto porque se está produciendo algo justo a la vez que lo consumes, habría que
añadir un extra semáforo???? He puesto un mutex pero no aregla na sos."""


