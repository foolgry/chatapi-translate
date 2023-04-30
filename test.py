from utils import get_global_config, translate_over_filter, from_messages_get_en
import asyncio
from pprint import pprint


async def main():
    print('=====测试: translator')
    text_to_translate = '''
这是代码：[YfeIdwzs8f] 你好
'''
    for name, translator in get_global_config()['translator'].items():
        print(name, ':')
        translate = translator.translate
        translated_text = await translate(text_to_translate)
        print(translated_text)
        
    print('=====测试: from_messages_get_en')
    marks = get_global_config()['marks']
    messages_en = from_messages_get_en([
        {
            "content": "test",
            "role": "system"
        },
        {
            "content": "你是谁？",
            "role": "user"
        },
        {
            "content": f'''
{marks["user_trans"]}hi
{marks["assistant_answer"]}hello
{marks["assistant_trans"]}你好
''',
            "role": "assistant"
        },
    ])
    pprint(messages_en)

    print('=====测试: translator_over_filter')
    text = 'Hello my world! `123`  ```abc``` '
    text = await translate_over_filter(text, translate=None)
    print(text)
    text = await translate_over_filter(text, translate=translate, role="assistant")
    print(text)


if __name__ == "__main__":
    asyncio.run(main())
