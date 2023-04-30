import base64
import aiohttp
import asyncio
import hashlib
import random
import hmac
from urllib.parse import quote
import base64
import time


class Translator:
    def __init__(self, conf):
        self.conf = conf
        self.semaphore = asyncio.Semaphore(conf['qps'])

    async def txTrans_async(self, q, appid, secretKey, fromLang='auto', toLang='zh'):
        if not q.strip():
            return ''

        params_dict = {
            # 公共参数
            'Action': 'TextTranslate',
            'Region': 'ap-guangzhou',
            'Timestamp': int(time.time()),
            'Nonce': random.randint(1, 1e6),
            'SecretId': appid,
            'Version': '2018-03-21',
            # 接口参数
            'ProjectId': 0,
            'Source': fromLang,
            'Target': toLang,
            'SourceText': q,
        }

        params_str = ''
        for key in sorted(params_dict.keys()):
            pair = '='.join([key, str(params_dict[key])])
            params_str += pair + '&'
        params_str = params_str[:-1]

        signature_raw = 'GETtmt.tencentcloudapi.com/?' + params_str
        hmac_code = hmac.new(bytes(secretKey, 'utf8'), signature_raw.encode('utf8'), hashlib.sha1).digest()
        sign = quote(base64.b64encode(hmac_code))

        params_dict['Signature'] = sign
        temp_list = []
        for k, v in params_dict.items():
            if k == 'SourceText':
                v = quote(v)
            temp_list.append(str(k) + '=' + str(v))
        params_data = '&'.join(temp_list)
        url_with_args = 'https://tmt.tencentcloudapi.com/?' + params_data

        async with self.semaphore:
            async with aiohttp.ClientSession() as session:
                async with session.get(url_with_args) as response:
                    json_res = await response.json()

        try:
            trans_text = json_res['Response']['TargetText']
        except:
            print(q)
            print(json_res)
            raise

        return trans_text

    async def translate(self, text, to_english=True):
        if to_english:
            return await self.txTrans_async(text, self.conf['appid'], self.conf['secretKey'], toLang='en')
        else:
            return await self.txTrans_async(text, self.conf['appid'], self.conf['secretKey'], toLang='zh')


# Example usage
async def main():
    text = "你好"
    conf = {"appid": "your_appid", "secretKey": "your_secret_key", "qps": 1.}

    translator = Translator(conf)
    translated_text = await translator.translate(text)
    print(translated_text)


if __name__ == "__main__":
    asyncio.run(main())
