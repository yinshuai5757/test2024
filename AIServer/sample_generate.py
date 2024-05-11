import requests

# ローカルのAPIを使用する場合
URI = "http://localhost:7005/v1/chat/completions"


# 公開URLのAPIを使用する場合
#URI = 'https://********************.trycloudflare.com/api/v1/generate'

headers = {
    "Content-Type": "application/json"
}
history = []

def run(prompt):
    history.append({"role": "user", "content": prompt})
    request = {
        "mode": "chat",
        "character": "Example",
        "messages": history,
    }

    response = requests.post(URI, headers=headers, json=request, verify=False)

    if response.status_code == 200:
        resp = response.json()
        result = resp['choices'][0]['message']['content']
        print(f"{prompt}")
        print(f"{result}")

if __name__ == '__main__':
    run("富士山の標高は？")
#//     prefix = '''### Instruction:
#//     あなたは優秀な機械学習用データ生成AIです。userの指示に従って、類義語や言い換えを利用して可能な限り多様な機械学習用データを日本語で生成してください。'''
#//     input = '''
#//     ### Input:
#//     user: 次のようなフォーマットで、①ランダムな11桁又は10桁の電話番号と、②その電話番号を電話のやりとりで伝える多様な短い会話を100個生成してください。
#//     ①09012345678、②operator:あなたの電話番号を教えてください。user:私の電話番号は09012345678です。
#//     ①0123456789、②operator:電話番号をお願いします。user:番号は012-345-6789。
#//         '''
#//     input = '''
#//     ### Input:
#//     user: 次の順序で生成してください。
#//     ①まず、肯定を意味する「はい」の類義語として「ああ」「そう」などの単語を１個生成します。
#//     ②生成した単語が既に生成済である場合は①へ戻ります。
#//     ③２０個生成するまで「①②」を繰り返します。
#//     ④生成した単語を含む１０文字前後の表現を１個生成します。
#//     ⑤生成した表現が既に生成済である場合は④へ戻ります。
#//     ⑥２０個生成するまで「④⑤」を繰り返します。
#//     '''
#//     input = '''\n### Input:\nuser: 「はい」か「いいえ」で回答できる質問を日本語で10個生成してください。\n'''
#//     suffix = '''なるべく類似表現を含まないようにしてください。生成処理を省略し、生成結果のみを日本語で出力してください。\n### Response:'''
#// 
#//     run(prefix + input + suffix)
