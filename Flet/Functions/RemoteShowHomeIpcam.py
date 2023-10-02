'''
1. Remotely connecting to Ip camera at home
2. Displaying the IPCAM video screen on flet window in real time
'''

import flet as ft
import base64
import cv2

ip = "<ip address>"
port = <port number>
user = "<ipcamera name for connection>"
password = "<ipcamera password for connection>"
url = f"rtsp://{user}:{password}@{ip}:{port}/11"
cap = cv2.VideoCapture(url)

class Countdown(ft.UserControl):
    def __init__(self):
        super().__init__()

    def did_mount(self):
        self.update_timer()

    def update_timer(self):
        while True:
            try:
                _, frame = cap.read()
                frame = cv2.resize(frame, (550,350), cv2.INTER_AREA)
                _, img_arr = cv2.imencode(".png", frame)
                img_b64 = base64.b64encode(img_arr)
                self.img.src_base64 = img_b64.decode("utf-8")
                self.update()
            except Exception as e:
                print(e)
                break
    
    def build(self):
        self.img = ft.Image(border_radius = ft.border_radius.all(10))
        return self.img

def height_changed(e):
    print(e.control.value)

# 페이지의 좌측부분 : 네이게이션 메뉴 생성 (시범적으로 생성해 봄, 내용관련없음)
left_sec = ft.NavigationRail(
    selected_index = 0,
    label_type = ft.NavigationRailLabelType.ALL,
    min_width = 140,
    min_extended_width = 200,
    leading = ft.FloatingActionButton(
        icon = ft.icons.CREATE,
        text = "ADD",
        bgcolor = ft.colors.LIGHT_BLUE_300
    ),
    group_alignment = -0.9,
    destinations = [
        ft.NavigationRailDestination(
            icon = ft.icons.FAVORITE_BORDER,
            selected_icon = ft.icons.FAVORITE,
            label = "FIRST" ),
        ft.NavigationRailDestination(
            icon_content = ft.Icon(ft.icons.BOOKMARK_BORDER),
            selected_icon_content = ft.Icon(ft.icons.BOOKMARK),
            label = 'SECOND' ),
        ft.NavigationRailDestination(
            icon = ft.icons.SETTINGS_OUTLINED,
            selected_icon_content = ft.Icon(ft.icons.SETTINGS),
            label_content = ft.Text("SETTINGS") )
    ],
    on_change = lambda e: print('Selected Destination: ',
                                e.control.selected_index )
)

# 페이지의 우측 부문 : ip camera 영상 디스플레이
right_sec = ft.Container(
    margin = ft.margin.only(bottom = 30),
    content = ft.Column(
        [
            ft.Card(
                elevation = 30,
                content = ft.Container(
                    bgcolor = ft.colors.WHITE,
                    padding = 10,
                    border_radius = ft.border_radius.all(10),
                    content = ft.Column(
                        [
                            Countdown(),
                            ft.Text(
                                "   Now, This Camera Is Running In Real Time..",
                                size = 15,
                                color = ft.colors.BLACK,
                                weight = ft.FontWeight.BOLD,
                                italic = True,
                                style = ft.TextThemeStyle.TITLE_MEDIUM
                            )
                        ]
                    )
                )
            ),
          # 영상화면 아래에 다른 기능의 card를 추가할 수 있음
            # ft.Card(
            #     elevation = 30,
            #     content = ft.Container(
            #         bgcolor = ft.colors.WHITE,
            #         padding = 10,
            #         border_radius = ft.border_radius.all(10),
            #         content = ft.Column(
            #             [
            #                 # ft.Text(
            #                 #     "Slider1", size = 15,
            #                 #     weight = 'bold', color = ft.colors.BLACK ),
            #                 # ft.Slider(
            #                 #     min = 400, max = 500,
            #                 #     on_change = lambda e: height_changed() ),
            #                 # ft.Text(
            #                 #     "Slider2", size = 15,
            #                 #     weight = 'bold', color = ft.colors.BLACK ),
            #                 # ft.Slider(
            #                 #     min = 400, max = 500,
            #                 #     on_change = lambda e: height_changed() )
            #             ]
            #         )
            #     )
            # )
        ],
        alignment = ft.MainAxisAlignment.CENTER,
        expand = True
    )
)

# 좌측과 우측 부분을 행방향으로 합치기 
section_all = ft.Container(
    ft.Row(
        [
            left_sec,
            ft.VerticalDivider(width = 1),
            right_sec
        ],
        width = 200,
        height = 300
    )
)

# 실행
def main(page: ft.Page):
    page.appbar = ft.AppBar(
        leading = ft.Icon(
            ft.icons.BEACH_ACCESS,
            color = ft.colors.BLUE,
            size = 40 ),
        leading_width = 40,
        title = ft.Text(
            "Real Time Home Video",
            size = 20, weight = "bold",
            color = ft.colors.BLACK),
        center_title = False,
        bgcolor = ft.colors.SURFACE_VARIANT
    )
    page.padding = 10
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = 'always'
    page.add(section_all)

if __name__ == "__main__":
    ft.app(target = main)
    cap.release()
    cv2.destroyAllWindows()
