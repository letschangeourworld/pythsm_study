### 카카오톡 자동 메시지 보내기
1. 개인PC에서 카카오톡 개인톡 또는 단체톡 메시지창을 띄워 놓는다.
2. 갠톡 or 단톡방 이름을 아래에 적어 준다. (아래 예시에서 단톡방 이름이 '존버 코린이 연구실'이다)
3. cText 변수에 보낼 메시지 내용을 적어 넣는다.
4. 반복 또는 예약 메시징을 하려면 threading 타이머에 초단위로 시간을 넣어서 조정한다.
5. 주피터 노트북에서 그냥 실행한다.
6. 예약전송을 해놓으려면 계속 실행해놔야 하는데
   아래 코드를 파일명.py 확장자로 저장해서 cmd 명령창에서 python 파일명.py 를 쳐서 실행해 놓는다. 끝 
 
~~~python
import time, win32con, win32api, win32gui
import datetime
import schedule
import threading

def printtest():
    now_time = '({})'.format(datetime.datetime.now().strftime('%y/%m/%d %H:%M:%S'))
    
    kakao = win32gui.FindWindow(None,"존버 코린이 연구실")
    chat = win32gui.FindWindowEx(kakao,None ,"RICHEDIT50W",None)  # 채팅창안 메세지 입력창 
    cText = "카톡 메시지 자동전송 테스트"
    win32api.SendMessage(chat,win32con.WM_SETTEXT,0,cText)         # 채팅창 입력
    win32api.PostMessage(chat,win32con.WM_KEYDOWN,win32con.VK_RETURN,0)
    win32api.PostMessage(chat,win32con.WM_KEYUP,win32con.VK_RETURN,0)   # 엔터키
    
    print(now_time + "60초마다 메시지 보내기")
    threading.Timer(60, printtest).start()
    
if __name__ == '__main__':
    printtest() 
~~~
