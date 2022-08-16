#モジュールをimport
import datetime, re, requests
import random 

# 論文の条件を設定する
QUERY = "ti:%22 Anomaly Detection %22 + OR + ti:%22 Machine Learning %22 + OR + ti:%22 Deep Learning %22"

# 翻訳のためのAPI KEY（DeepL翻訳版）
DeepL_API_KEY = '9b00a65e-2c76-935d-2e06-f1dcb2eef3ab:fx'

# IFTTTを用いてarXivとLINEを繋ぐ
# webhook POST先URL
API_URL = "https://maker.ifttt.com/trigger/Arxiv2Line/with/key/dA8MFn-L3SihTEa0GUeL9E"

#欲しい論文数
num_papers = 5

#　指定したHTMLtagの情報を返す e.g. Input :<tag>XYZ </tag> -> Output: XYZ
def parse(data, tag):
    pattern = "<" + tag + ">([\s\S]*?)<\/" + tag + ">"
    if all:
        obj = re.findall(pattern, data)
    return obj

#論文を探してきてwebhooksにPOSTする関数
def search_and_send(query, api_url):
    while True:

        url = 'http://export.arxiv.org/api/query?search_query=' + query + '&start=0&max_results=1000&sortBy=submittedDate&sortOrder=descending'
        #　arXiv APIから指定したURLの情報を受け取る
        data = requests.get(url).text

        # 各論文ごとに分ける
        entries = parse(data, "entry")
        
        entries = random.sample(entries, k=num_papers)

        for entry in entries:

          # Parse each entry
          url = parse(entry, "id")[0]

          # 情報の分離
          title = parse(entry, "title")[0]
          abstract = parse(entry, "summary")[0]
          date = parse(entry, "published")[0]

          # abstの改行を取る
          abstract = abstract.replace('\n', '')

          # deepLで日本語に翻訳
          # https://deepblue-ts.co.jp/nlp/deepl-api-python/ を参照
          # DeepLのURLクエリに仕込むパラメータを作っておく
          params = {"auth_key": DeepL_API_KEY, "text": abstract, "source_lang": 'EN', "target_lang": 'JA'}
          # DeepLに翻訳してもらう
          request = requests.post("https://api-free.deepl.com/v2/translate", data=params)
          #Pro版ならクリエを出すURLは、https://api.deepl.com/v2/translate
          result = request.json()
          abstract_jap = result["translations"][0]["text"]
          message = "\n".join(["<br>Title:  " + title, "<br><br>URL: " + url, "<br><br>Published: " + date, "<br><br>JP_Abstract: " + abstract_jap]) 

          # webhookへPost 
          response = requests.post(api_url, data={"value1": message})

        messageend = "今日の論文は以上です。"
        requests.post(api_url, data={"value1": messageend})
        return 0

def main(event, context):
    # setup 
    # IFTTT APIを設定
    api_url = API_URL
    # arXiv APIのクエリ
    query = QUERY

    # start 
    # LINEに時間を送る
    dt = datetime.datetime.now().strftime("%Y/%m/%d") 
    requests.post(api_url, data={"value1": dt})

    # 今日の論文をLINEに送る
    search_and_send(query, api_url)

# main関数を実行(Cloud functionsでは不要)
# main()