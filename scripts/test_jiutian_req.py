import http.client
import json

conn = http.client.HTTPSConnection("jiutian.10086.cn")
payload = json.dumps({
   "modelId": "jiutian-qianwen",
   "prompt": "你是什么大模型？",
   "params": {
      "temperature": 0.8,
      "top_p": 0.95
   },
   "history": [],
   "stream": False
})
headers = {
   'Authorization': 'Bearer **token**',
   'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
   'Content-Type': 'application/json'
}
conn.request("POST", "/largemodel/api/v1/completions", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))