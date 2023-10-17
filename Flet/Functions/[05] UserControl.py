import flet as ft

class Counter(ft.UserControl):
    def build(self):
        self.counter = 0
        text = ft.Text(str(self.counter))

        # build함수의 하위함수로 배치하면 build함수의 지역변수를 가져올 수 있음
        # self를 사용하지 않아도 됨
        def add_click(e):
            self.counter += 1
            text.value = str(self.counter)  
            self.update()
        
        return ft.Row(
            [
                text,
                ft.ElevatedButton(
                    "Add",
                    on_click = add_click )
            ]
        )

def main(page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 30
    page.window_width = 580
    page.window_height = 740
    page.add(Counter(), Counter())

ft.app(target=main)

############################################################

import flet as ft
import time, threading

'''
process : 프로그램이 메모리에 올라가서 실행 중인 것을 말함
thread : process의 실행 단위를 말함, process는 최소 1개 이상의 thread를 갖음
daemon thread : main thread가 종료될 때, 자신의 실행상태와 관계없이 종료시키는 thread
threading.Thread(target = None, args = (), daemon = None)
  - target : run() 이나 start() method에 의해 호출되는 callable object
  - args : 호출된 target argument 형식이 list or tuple
threading 라이브러리 : 여러 개의 thread 호출 처리를 위해 사용
'''

class Countdown(ft.UserControl):
    def __init__(self, seconds): # Countdown class의 Construnctor 생성하여 재사용 가능하게 하기
        super().__init__()       # 항상 UserControl class의 Constructor로 초기화시킨 후에 재사용
        self.seconds = seconds   # seconds 변수 초기화

    def did_mount(self):
        self.running = True   # running boolean 변수생성
        self.th = threading.Thread(
            target = self.update_timer,
            args = (),
            daemon = True )
        self.th.start()       # Multi-threading 실행시작

    def will_unmount(self):   # threading 종료
        self.running = False

    def update_timer(self):   # threading target 객체
        while self.seconds and self.running:
            mins, secs = divmod(self.seconds, 60)
            self.countdown.value = "{:02d}:{:02d}".format(mins, secs)
            self.update()
            time.sleep(1)
            self.seconds -= 1

    def build(self):
        self.countdown = ft.Text()   # 카운트다운 숫자를 ft.Text() 클래스로 입혀 줌
        return self.countdown        # ft.Text()로 입힌 카운트다운 숫자를 반환

def main(page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 30
    page.window_width = 580
    page.window_height = 740
    page.add(Countdown(120), Countdown(60))

ft.app(target=main)
