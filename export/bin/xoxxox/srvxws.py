import os
import json
import argparse
import asyncio
from aiohttp import web
from xoxxox.params import Config
from xoxxox.shared import Custom

#---------------------------------------------------------------------------

async def ressys(datreq):
  global diccnf, dicprm, prcsub, sectmo
  try:
    dicres={"status": "1"}
    dicreq = await datreq.json()

    if 'config' in dicreq:
      diccnf = Custom.update(dicreq["config"], dicprm)
    else:
      diccnf["usrapp"] = dicreq["usrapp"]
      diccnf["envapp"] = dicreq["envapp"]
      diccnf["script"] = dicreq["script"]

    if prcsub and prcsub.returncode is None:
      prcsub.terminate()
      await prcsub.wait()
    if diccnf["script"] != "":
      prcsub = await asyncio.create_subprocess_exec(
        "/opt/common/bin/xoxxox/runapp.sh", diccnf["usrapp"], diccnf["envapp"], diccnf["script"],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
      )
      try:
        stdout, stderr = await asyncio.wait_for(
          prcsub.communicate(),
          timeout=sectmo,
        )
        if prcsub.returncode != 0:
          dicres={"status": "0", "errors": stderr.decode()}
      except asyncio.TimeoutError:
        pass
  except Exception as e:
    dicres={"status": "0", "errors": str(e)}
  return web.Response(
    text=json.dumps(dicres),
    content_type="application/json",
  )

#---------------------------------------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument("--secure", default="0")
parser.add_argument("--svport", type=int, default="80")
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

sectmo = 5 # タイムアウト（正常に起動と判断するまでの時間）
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
