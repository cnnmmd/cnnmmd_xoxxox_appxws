#---------------------------------------------------------------------------
# 参照

import aiohttp
from xoxxox.libmid import LibMid

#---------------------------------------------------------------------------
# 処理：Ｘウィンドウサーバを起動する

class PrcXws:

  # 変数
  oldcfg = ""

  # 実行
  @staticmethod
  async def cnnprc(datorg, server, config):

    if config != PrcXws.oldcfg:
      async with aiohttp.ClientSession() as sssweb:
        async with sssweb.post(server + "/sys", json={"config": config}) as datres:
          dicres = await datres.json()
      PrcXws.oldcfg = config
    return ({"status": "1"})

LibMid.dicprc["xoxxox.PrcXws.cnnprc"] = {"frm": "xoxxox_libxws.PrcXws.cnnprc", "arg": ["keymmd"], "cnf": ["server", "config"], "syn": False}
