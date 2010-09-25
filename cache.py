#coding: utf-8 -*-.
import memcache
import pickle

class Cache:

    def __init__(self, servers=['localhost:11211']):
        """
        Conección a los servidores de cache

        hosts - Lista de server:port
        ej: ['localhost:11211', 'localhost:11212']
        """
        self.mc = memcache.Client(servers, debug=0)

    def set(self, key, obj):
        self.mc.set(key, pickle.dumps(obj))

    def get(self, key):
        s = self.mc.get(key)
        if s:
            return pickle.loads(s)
        return None



if __name__ == "__main__":

    class Person:
        def __init__(self, id, name, age):
            self.id = id
            self.name = name
            self.age = age

    for i in range(10):
        key = "hola:"+ str(i)
        cacheClient = Cache(['localhost:11211','localhost:11212'])
        persona = cacheClient.get(key)
        if not persona:
            pepe = Person(key, "pepe", "22")
            cacheClient.set(pepe.id, pepe)
            print "guardado en cache!"
            print pepe.name
            print pepe.age
        else:
            print persona.name
            print persona.age

    cacheClient = Cache(['localhost:11211','localhost:11212'])
    cacheClient.mc.incr("hola:*")
