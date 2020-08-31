import asyncio
import base64
import string
import random
import redis
from aiohttp import web
import aiohttp_session
import aiohttp_jinja2
import jinja2
from cryptography import fernet
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import s4_kayit

## S 4 L E H WEB SERVER 



web_server_ip = "127.0.0.1"
web_server_port = 8080
web_server_adress = f"http://{web_server_ip}:{web_server_port}"
guncelleme_zamani = 12312512562112


routes = web.RouteTableDef()
routes.static("/files", "files")
xml = f"""<?xml version="1.0" ?>
<cross-domain-policy>
    <allow-access-from domain="*.{web_server_ip}" />
</cross-domain-policy>"""






def get_level(exp):
    expSum = 0
    i = 0
    while expSum <= exp:
        i += 1
        expSum += i * 50
    return i


@routes.get("/")
async def index(request):
    session = await aiohttp_session.get_session(request)
    context = {}
    context["kayitli_kullanici"] = app["redis"].get(f"uids")
    if "token" not in session:
        context["logged_in"] = False
    else:
        context["logged_in"] = True
        context["token"] = session["token"]
        context["update_time"] = guncelleme_zamani
        context["gameid"] = session["uid"]
        uid = session["uid"]
        context["isim"] = app["redis"].get(f"uid:{uid}:ad_soyad")
    return aiohttp_jinja2.render_template("index.html", request,
                                          context=context)

@routes.get("/kayit.slh")
async def index(request):
    context = {}
    return aiohttp_jinja2.render_template("kayit.html", request, context=context)



@routes.post("/giris.slh")
async def giris(request):
    session = await aiohttp_session.new_session(request)
    data = await request.post()
    eposta = data["eposta"]
    sifre = data["sifre"]
    uid = False
    uids = app["redis"].get(f"uids") 
    uids = int(uids) + 10
    v = 1
    for i in range(1, int(uids)):
      if app["redis"].get(f"uid:{i}:mail") == eposta:
        v = int(i)
        break
    if app["redis"].get(f"uid:{v}:panelsifre") == sifre:
        uid = True
    if uid == True:
        session["uid"] = int(v)
        session["token"] = app["redis"].get(f"uid:{v}:sifre")
    raise web.HTTPFound("/")


@routes.post("/sifre_degistir.slh")
async def sifre_degistir(request):
    session = await aiohttp_session.get_session(request)
    data = await request.post()
    sifre = data["sifre"]
    yeni_sifre = data["yeni_sifre"]
    v = session["uid"]
    sifre_d = "Şifre eşleşmiyor."
    if sifre == app["redis"].get(f"uid:{v}:panelsifre"):
        sifre_d = "Şifreniz başarılı şekilde değiştirildi."
        app["redis"].set(f"uid:{v}:panelsifre", yeni_sifre)
    return web.Response(text=sifre_d)



@routes.post("/sifirla.slh")
async def sifre_degistir(request):
    session = await aiohttp_session.get_session(request)
    data = await request.post()
    sifre = data["sifre"]
    v = session["uid"]
    sifre_d = "Şifre eşleşmiyor."
    if sifre == app["redis"].get(f"uid:{v}:panelsifre"):
        s4_kayit.sifirla(app["redis"], uid)
        sifre_d = "Hesabınız başarılı şekilde sıfırlandı."
    return web.Response(text=sifre_d)



def random_string(string_length=20):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(string_length))

@routes.get("/basarisiz.slh")
async def basarisiz(request):
    context = {}
    return aiohttp_jinja2.render_template("basarisiz.html", request,
                                          context=context)

@routes.post("/kayit_ol.slh")
async def kayit_ol(request):
    data = await request.post()
    ad_soyad = data["ad_soyad"]
    eposta = data["eposta"]
    sifre = data["sifre"]
    bbcode = random_string()
    uids = app["redis"].get("uids")
    devam = True
    for i in range(1, int(uids)):
        if app["redis"].get(f"uid:{i}:mail") == eposta:
            devam = False
            break
    if devam == True:
      s4_uid, s4_sifre = s4_kayit.hesap_olustur(app["redis"], eposta, sifre, bbcode, ad_soyad)
      session = await aiohttp_session.new_session(request)
      session["uid"] = s4_uid
      session["token"] = s4_sifre
      raise web.HTTPFound("/")
    else:
      return web.Response(text="Aynı epostaya sahip bir hesap mevcut.")

@routes.get("/cikis.slh")
async def cikis(request):
    session = await aiohttp_session.get_session(request)
    if "token" in session:
        del session["token"]
        del session["uid"]
    raise web.HTTPFound("/")

@routes.get("/prelogin")
async def prelogin(request):
    if "sid" not in request.query:
        raise web.HTTPClientError()
    try:
        uid = int(request.query["sid"])
    except ValueError:
        raise web.HTTPClientError()
    exp = int(app["redis"].get(f"uid:{uid}:exp"))
    return web.json_response({"user": {"bannerNetworkId": None, "reg": 0,
                                       "paymentGroup": "",
                                       "preloginModuleIds": "", "id": uid,
                                       "avatariaLevel": get_level(exp)}})

@routes.post("/social")
async def social(request):
    data = await request.post()
    if not data["method"]:
        raise web.HTTPClientError()
    if data["method"] == "getTestUsers":
        return web.json_response({"uids": [str(data["user_id"])]})
    elif data["method"] in ["getFriends", "getAppFriends"]:
        return web.json_response([])
    elif data["method"] == "getProfiles":
        return web.json_response([{"id": data["uids"]}])


@routes.get("/appconfig.xml")
async def appconfig(request):
    session = await aiohttp_session.get_session(request)
    if "uid" not in session:
        raise web.HTTPUnauthorized()
    context = {"token": session["token"], "uid": session["uid"],
               "ip": web_server_ip,
               "address": web_server_adress}
    return aiohttp_jinja2.render_template("appconfig.xml", request,
                                          context=context)


@routes.get("/crossdomain.xml")
async def crossdomain(requst):
    return web.Response(text=xml)


async def main():
    global app
    app = web.Application()
    app.add_routes(routes)
    app["redis"] = redis.Redis(decode_responses=True)
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    aiohttp_session.setup(app, EncryptedCookieStorage(secret_key))
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("www"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 8080)
    await site.start()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
