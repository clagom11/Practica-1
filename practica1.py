#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 13:03:06 2023

@author: prpa
"""

from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array, Manager
from time import sleep
from random import random, randint


N = 5
NPROD = 4




def delay(factor = 3):
    sleep(random()/factor)

def add_data(storage, proceso, index, pid, data, mutex):
    mutex.acquire()
    try:
        storage[index.value] = data
        proceso[index.value] = pid #así en la misma posición que su dato, podemos ver qué proceso lo añadió.
        delay(6)
        index.value = index.value + 1
    finally:
        mutex.release()
        
def add_menos_uno(storage, proceso, index, pid, mutex):
    mutex.acquire()
    try:
        storage[index.value] = -1
        proceso[index.value] = pid #así en la misma posición que su dato, podemos ver qué proceso lo añadió.
        delay(6)
        index.value = index.value + 1
    finally:
        mutex.release()



def producer(storage, proceso, index, empty, non_empty, mutex):
    producto = 0
    for v in range(N):
        #print (f"producer {current_process().name} produciendo")
        delay(6)
        num = randint(1,5)
        producto+=num
        empty.acquire()
        add_data(storage, proceso, index, int(current_process().name.split('_')[1]),
                 producto, mutex)
        non_empty.release()
        print (f"producer {current_process().name} almacenado {v}" + '\n')
    empty.acquire()
    add_menos_uno(storage, proceso, index, int(current_process().name.split('_')[1]), mutex)
    non_empty.release()


def merge(storage, proceso, index, empty, non_empty, mutex, lista):
    for i in range(NPROD):
        non_empty[i].acquire()
    
    
    minimo = max(storage)#número para inicializar y que siempre haya un elemento en storage que sea más pequeño y pase a ser el mínimo, sin ser -1, por las condiciones de después.
    print(minimo)
    while minimo != -1:
        pos = 0
        for j in range(len(storage)): #hallamos el mínimo y vamos contando los -1
            print("storage:",storage[j]) 
            if (storage[j] >= 0) and (storage[j] <= minimo):
                minimo = storage[j] 
                pos = j
        
        index.value = pos
        p = proceso[pos] #para averiguar a qué proceso pertenece 
        print("Elemento añadido: ", minimo ,", perteneciente al proceso: " , p , '\n') 
        storage[pos] = -2
        lista.append((minimo,p))
        print(lista)
        minimo = max(storage)
        
        empty[p].release()
        delay()
        non_empty[p].acquire() #tenemos que esperar a q el proceso p obtenga un nuevo producto.
    
def main():
    storage = Array('i', NPROD)
    proceso = Array('i', NPROD)
    index = Value('i', 0)
    lista = []
    
    for i in range(NPROD):
        storage[i] = -1
    print ("almacen inicial", storage[:], "indice", index.value)

    non_empty = []
    empty = []
    mutex = Lock()
    
    for j in range(NPROD):
        non_empty.append(Semaphore(0))
        empty.append(BoundedSemaphore(1)) #solo hay un producto cada vez.

    prodlst = [ Process(target=producer,
                        name=f'prod_{i}',
                        args=(storage, proceso, index, empty[i], non_empty[i], mutex))
                for i in range(NPROD) ]

    m = Process(target=merge,
                      args=(storage,proceso, index, empty, non_empty, mutex, lista))
               

    for p in prodlst:
        p.start()
    m.start()

    for p in prodlst:
        p.join()
    m.join


if __name__ == '__main__':
    main()
    
