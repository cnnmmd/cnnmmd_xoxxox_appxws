import os
import json
import argparse
import asyncio
from aiohttp import web
from xoxxox.params import Config
from xoxxox.shared import Custom

#---------------------------------------------------------------------------

async def ressys(datreq):
  global diccnf, dicprm, prcsub
  dicreq = await datreq.json()
  diccnf = Custom.update(dicreq["config"], dicprm)
  if prcsub and prcsub.returncode is None:
    prcsub.terminate()
    await prcsub.wait()
  if diccnf["script"] != "":
    prcsub = await asyncio.create_subprocess_exec(
      "/opt/common/bin/xoxxox/runapp.sh", diccnf["usrapp"], diccnf["envapp"], diccnf["script"]
    )
  return web.Response(
    text=json.dumps({"status": "1"}),
    content_type="application/json",
  )

#---------------------------------------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument("--secure", default="0")
parser.add_argument("--svport", type=int, default="80")
parser.add_argument("--config")
parser.add_argument("--adraco", type=str) # default: cnfnet
parser.add_argument("--pthcrt", type=str) # default: cnfnet
parser.add_argument("--pthkey", type=str) # default: cnfnet
objarg = parser.parse_args()

dicnet = Custom.update(Config.cnfnet, {k: v for k, v in vars(objarg).items() if v is not None})
dicprm = {k: v for k, v in vars(objarg).items() if v is not None}

dicprm.pop("secure")
dicprm.pop("svport")

secure = objarg.secure
svport = objarg.svport

adrsys = "/sys"

#---------------------------------------------------------------------------

diccnf = {}
prcsub = None
appweb = web.Application()
appweb.add_routes([web.post(adrsys, ressys)])
if secure == "0":
  web.run_app(appweb, port=svport)
if secure == "1":
  import ssl
  sslcon = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
  sslcon.load_cert_chain(dicnet["pthcrt"], dicnet["pthkey"])
  web.run_app(appweb, port=svport, ssl_context=sslcon)
