import aiohttp
import asyncio
import json
from aiolimiter import AsyncLimiter
import re


class Translator:
    def __init__(self, conf):
        self.conf = conf
        self.limiter = AsyncLimiter(conf['qps'], 1)

    async def caiyun_translate_async(self, source, trans_type='en2zh', request_id='demo'):
        url = "http://api.interpreter.caiyunai.com/v1/translator"
        headers = {
            'content-type': "application/json",
            'x-authorization': "token " + self.conf['api_key'],
        }
        payload = {
            "source": source,
            "trans_type": trans_type,
            "request_id": request_id,
            "detect": True,
        }

        async with aiohttp.ClientSession() as session:
            async with self.limiter:
                try:
                    async with session.post(url, headers=headers, json=payload) as response:
                        result_all = await response.text()
                        result = json.loads(result_all)
                except Exception as e:
                    result = {'error': e}

        return result

    async def translate(self, text, to_english=True):
        if to_english:
            trans_type = 'auto2en'
        else:
            trans_type = 'auto2zh'

        text = text.split('\n')

        result = await self.caiyun_translate_async(text, trans_type=trans_type)
        if 'target' in result:
            t = '\n'.join(result['target'])
            # 去除标记符号的前后空格,防止替换问题, 与 utils.generate_random_id 保持一致
            t = re.sub(r'(?<=\[) (?=[0-9a-zA-Z]{10} \])', '', t)
            t = re.sub(r'(?<=\[[0-9a-zA-Z]{10}) (?=\])', '', t)
            return t
        else:
            print(result)
            return None


# Example usage
async def main():
    text = """测试: [YfeIdwzs8f]
def abc():
    treturn '你好'
结束"""
    conf = {"api_key": "your_token", "qps": 1.}

    translator = Translator(conf)
    translated_text = await translator.translate(text)
    print(translated_text)


if __name__ == "__main__":
    asyncio.run(main())
