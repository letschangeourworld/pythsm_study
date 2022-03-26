카톡

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
