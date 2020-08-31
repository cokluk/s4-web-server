import string
import random


def hesap_olustur(redis, eposta, sifre, bbcode, ad_soyad):
    
    redis.incr("uids")
    uid = redis.get("uids")
    pipe = redis.pipeline()
    pipe.set(f"auth:{bbcode}", uid)
    pipe.set(f"uid:{uid}:slvr", 1000)
    pipe.set(f"uid:{uid}:gld", 6)
    pipe.set(f"uid:{uid}:ad_soyad", ad_soyad)
    pipe.set(f"uid:{uid}:sifre", bbcode)
    pipe.set(f"uid:{uid}:mail", eposta)
    pipe.set(f"uid:{uid}:panelsifre", sifre)
    pipe.set(f"uid:{uid}:enrg", 100)
    pipe.set(f"uid:{uid}:exp", 500000)
    pipe.set(f"uid:{uid}:emd", 0)
    pipe.set(f"uid:{uid}:lvt", 0)
    pipe.sadd(f"uid:{uid}:items", "blackMobileSkin")
    pipe.rpush(f"uid:{uid}:items:blackMobileSkin", "gm", 1)
    pipe.sadd(f"rooms:{uid}", "livingroom")
    pipe.rpush(f"rooms:{uid}:livingroom", "#livingRoom", 1)
    for i in range(1, 6):
        pipe.sadd(f"rooms:{uid}", i)
        pipe.rpush(f"rooms:{uid}:{i}", f"Oda {i}", 2)
    pipe.execute()
    return (uid, bbcode)

def sifirla(redis, uid):
    pipe = redis.pipeline()
    pipe.set(f"uid:{uid}:slvr", 1000)
    pipe.set(f"uid:{uid}:gld", 6)
    pipe.set(f"uid:{uid}:enrg", 100)
    pipe.delete(f"uid:{uid}:trid")
    pipe.delete(f"uid:{uid}:crt")
    pipe.delete(f"uid:{uid}:hrt")
    pipe.delete(f"uid:{uid}:wearing")
    pipe.delete(f"uid:{uid}:appearance")
    for item in redis.smembers(f"uid:{uid}:items"):
        pipe.delete(f"uid:{uid}:items:{item}")
    pipe.delete(f"uid:{uid}:items")
    for room in redis.smembers(f"rooms:{uid}"):
        for item in redis.smembers(f"rooms:{uid}:{room}:items"):
            pipe.delete(f"rooms:{uid}:{room}:items:{item}")
        pipe.delete(f"rooms:{uid}:{room}:items")
        pipe.delete(f"rooms:{uid}:{room}")
    pipe.delete(f"rooms:{uid}")
    pipe.sadd(f"uid:{uid}:items", "blackMobileSkin")
    pipe.rpush(f"uid:{uid}:items:blackMobileSkin", "gm", 1)
    pipe.sadd(f"rooms:{uid}", "livingroom")
    pipe.rpush(f"rooms:{uid}:livingroom", "#livingRoom", 1)
    for i in range(1, 6):
        pipe.sadd(f"rooms:{uid}", i)
        pipe.rpush(f"rooms:{uid}:{i}", f"Комната {i}", 2)
    pipe.execute()