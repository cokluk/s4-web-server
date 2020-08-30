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