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
tam = 4 #tamaño fijo del buffer de cada productor.



def delay(factor = 3):
    sleep(random()/factor)

"""Añadir los productos cambia un poco respecto al anterior ejercicio de la práctica, ya que ahora
lo que vamos a tener es un storage con tamaño NPROD * tam y dentro de dicho storage, las tam primeras
posiciones pertenecerán al proceso 0, las tam siguientes al 1... y así sucesivamente. Para asegurarnos de
que cada elemento está siendo colocado en su "franja" de posiciones correspondiente tenemos, a parte del
semáforo que controla que no entren más de tam productos por proceso, dentro de esta función add_data,
un bucle que comprueba la primera posición (dentro de la franja) que no está vecía (no sea -2), para
colocar ahí el nuevo dato"""
def add_data(storage, pid, data, mutex):
    mutex.acquire()
    try:
        indice = pid * tam #para añadir los productos en la franja del storage correspondiente al proceso en el que estamos.
        cont = 0
        
        while storage[cont + indice] != -2:
            cont += 1
        storage[cont + indice] = data
        cont = 0
        
        delay(6)

    finally:
        mutex.release()

"""Igual que en la parte anterior de la práctica, se llama a esta función cuando se acaba de producir.
Como en este caso puede ocurrir que, aunque se termine el proceso, aún hay elementos en el buffer,
tenemos que colocar el -1 en la primera casilla vacía, empleando la misma técnica que en el add_data"""
def add_menos_uno(storage,pid, mutex):
    mutex.acquire()
    try:
        indice = pid * tam
        cont = 0
        
        while storage[cont + indice] != -2:
            cont += 1
        storage[cont + indice] = -1 #colocamos el -1 en la posición correspondiente, cuando llegue al principio de cada franja, todo lo demás serán -2 y ya no habrá más productos de este proceso.
        cont = 0 
        delay(6)

    finally:
        mutex.release()


"""Esta función sigue actuando del mismo modo que en el caso de que solo se produciese un producto por 
proceso, como es lógico."""
def producer(storage, empty, non_empty, mutex):
    producto = 0
    for v in range(N):
        delay(6)
        empty.acquire()
        num = randint(1,5)
        producto+=num
        

        add_data(storage, int(current_process().name.split('_')[1]),
                 producto, mutex)
        non_empty.release()
        print (f"producer {current_process().name} almacenado {producto}" + '\n')
    empty.acquire()
    add_menos_uno(storage, int(current_process().name.split('_')[1]), mutex)
    non_empty.release()

"""Para consumir un producto se sigue con la misma dinámica de escoger el mínimo, pero en este caso
fijándonos en el primer producto obtenido por cada proceso. Una vez consumido, si tenemos más elementos
de productor en el buffer, éstos han de moverse a la izquierda, para que el siguiente producto pase a 
ser el que tenemos en cuenta para compararlo con los demás y hallar el mínimo. Además añadiremos un
-2 al final, dejando un nuevo hueco vacío."""
def merge(storage, empty, non_empty, mutex, lista):
    print("almacen:", storage)
    for i in range(NPROD):
        non_empty[i].acquire()
    
    
    minimo = max(storage) #así podremos encontrar otro que sea menor que él, a no ser que todos los demás sean -1.
    print("Mínimo: ", minimo)
    while minimo != -1:
        pos = 0
        for j in range(0,len(storage),tam): #siempre nos fijamos en el primero que ha producido cada productor, por eso vamos de K en K.
            #hallamos el mínimo
 
            if (storage[j] >= 0) and (storage[j] <= minimo): 
                minimo = storage[j]
                pos = j
        
        productor = pos // tam #para averiguar a que proceso pertenece el elemento añadido.
        print("Elemento añadido: ", minimo ,", perteneciente al proceso: " , productor , '\n') 
        
        lista.append((minimo,productor)) #añadimos el mínimo a la lista 
        print("Lista de elementos del merge: ", lista)
        
        #y ahora procedemos a consumirlo de storage, para lo que hacemos lo siguiente:
        for k in range(pos, pos + tam): #movemos todos los elementos del buffer a la izquierda y añadimos un -2 al final.
            
            if k == pos + tam - 1:  #cuando nos encontramos en el último caso, tenemos que añadir en esa posición un -2.
                storage[k] = -2
            else:
                storage[k] = storage[k+1]
                
        #Descomentar si se quiere ver el estado del almacén en cada momento.
        #for j in range(len(storage)):
            #print("storage: (",storage[j],", ", j, ")")  #para ver cómo se nos queda el storage después de consumir el elemento correspondiente.
                


        minimo = max(storage)
        
        empty[productor].release() #para indicar que se ha consumido un producto del productor correspondiente.
        delay()
        non_empty[productor].acquire() 
    
def main():
    storage = Array('i', NPROD * tam) #almacén del tamaño adecuado.
    lista = []
    
    for i in range(NPROD * tam): #inicializamos el almacén para que esté vacío
        storage[i] = -2
    print ("almacen inicial", storage[:])

    non_empty = []
    empty = []
    mutex = Lock()
    
    for j in range(NPROD):
        non_empty.append(Semaphore(0))
        empty.append(BoundedSemaphore(tam)) #puede haber más de un producto cada vez.

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




