import requests

# ローカルのAPIを使用する場合
URI = "http://localhost:7005/v1/chat/completions"

X生年月日 = "昭和６０年２月１日"
X経歴 = "平成２7年合格。翌年免許取得。"

user_message = f"原告は、{X生年月日}に生まれた。[{X経歴}を自然な文章で紹介]"
stop = ["[", "<"]
headers = {
    "Content-Type": "application/json"
}
data = {
    "model": "gpt-3.5-turbo",
    "messages": [
    {"role": "system", "content": "あなたは、userが与えたFORMATの内容を修正して返すAIです。\n    修正方法は次のとおりです。\n    ①userはあなたに、FORMAT、及びCASE_MEMOを与えます。\n    ②CASE_MEMOは「X経歴=平成２８年に宅建に合格」のように記載されています。これは、「'X経歴'という変数に文字列'平成２８年に宅建に合格'を代入する」という意味です。\n    ③FORMATには「原告には{X経歴}という経歴がある。」のような記載があります。この場合、あなたは変数部分を展開し「原告には平成２８年に宅建に合格という経歴がある。」のように修正して返します。\n    ④FORMATには「[{X経歴}を自然な文章で紹介]」のような記載があります。この場合、'['と']'で囲まれた部分はあなたへの指示です。その指示に従って、例えば「原告は平成２８年に宅地建物取引士の試験に合格している。」のように修正します。\n    ⑤算用数字はすべて全角文字に修正します。\n    ⑥最後に、あなたはFORMATをCASE_MEMOに基づいて処理した結果をuserに返します。"},
    {"role": "user", "content": "FORMAT: 原告は、『昭和６０年２月１日』に生まれた。[『平成２８年に宅建に合格。翌年免許取得。』を自然な文章で紹介]\nCASE_MEMO: 訴状（残業代）.plt\n*当事者\nX=甲野次郎\nX生年月日=昭和６０年２月１日\nX入社日=平成２７年４月１日\nX退職=令和３年４月３０日\nX経歴=平成２８年に宅建に合格。翌年免許取得。\nX業務=経理\nY住所=千葉県\nY業務=建築\n早出が必要な事情=所定出勤時間は午前９時だが社長が早朝出勤奨励。\n証拠(労働時間)=甲１：手帳"},
    {"role": "assistant", "content": "原告は、昭和６０年２月１日に生まれた。資格としては、平成２８年に宅建に合格している。"},
    {"role": "user", "content": user_message}
  ],
  "stop": stop
}

response = requests.post(URI, headers=headers, json=data, verify=False)

if response.status_code == 200:
    resp = response.json()
    result = resp['choices'][0]['message']['content']
    print(result)
else:
    print("Failed to get response")