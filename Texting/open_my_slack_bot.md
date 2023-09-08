### Slack 메신저에 정보를 자동으로 보내기 위한 chat 봇 만들기

#### ◈ 내 중요정보 json file로 저장
~~~python
import json           # 텍스트를 json파일로 저장할 때 사용함
import requests       # 슬랙 앱 접속에 필요함

file_path = "./token.json"                # 토큰이 저장된 파일위치 및 파일명
mydata = {}                               # 빈 사전 형태 생성
mydata['token'] = '내 토큰 정보 입력'      # 사전에 token이라는 이름으로 토큰정보 저장
print(mydata)                             # 저장 확인해 보기

# file_path 위치 및 파일명으로 json확장자로 저장 
with open(file_path, 'w') as outfile:     # 'w' : 저장, 'r' : 불러오기
    json.dump(mydata, outfile)            # mydata사전을 outfile을 열어서 저장
~~~

#### ◈ 봇을 만들어서 내 메신저로 메시지 보내기
~~~python
# 슬랙 메신저에 메시지를 보내기 위해서 접속하는 함수생성
# token   : 슬랙사이트에서 주어진 본인 고유ID
# channel : 메신저 대화방 이름
# text    : 보내고자 하는 메시지
def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
                             headers = {"Authorization":"Bearer " + token},
                             data = {"channel" : channel,"text" : text})
    print(response)   # 메시지 송신완료 신호

slack_path = "./token.json"   # 내 PC에서 내 토큰 불러오기
# 사전형식으로 저장했기 때문에 사전을 통째로 불러옴
with open(slack_path, 'r') as json_file:
    slack_dict = json.load(json_file)

mytoken = slack_dict['token']  # 사전에서 token명으로 된 정보 가져오기
post_message(mytoken,
             "#investment",
             "안녕! 반가워. 나는 정보를 자동으로 보내는 봇이야!")  # 메신저에서 메시지 확인해보기
~~~

![bot_image](https://user-images.githubusercontent.com/50024239/140595877-b120d1f1-a8e6-44ed-9b3d-1747195a8fbe.png)
