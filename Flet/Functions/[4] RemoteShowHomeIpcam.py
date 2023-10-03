'''
1. Remotely connecting to Ip camera at home
2. Displaying the IPCAM video screen on flet window in real time
'''
import flet as ft
import base64
import cv2

'''
- Router Configuration Example -
1) public IP address : 222.129.207.155 (Home router port-forwarding only for IP camera)
2) public IP port : 51234              (Home router port-forwarding only for IP camera)
3) private IP address : 192.168.0.55   (IP camera address designated by Home router)
4) private IP port : 554               (IP camera port designated for rtsp)

When remotely connecting through 222.129.207.155:51234 on web,
network is as follows:

222.129.207.155:51234 (from outside) <-----> home router <-----> 192.168.0.55:554 (IP camera)
'''

ip = "222.129.207.155"    # public IP address
port = 51234              # public port
user = "<user name of ipcamera>"
password = "<password of ipcamera>"
url = f"rtsp://{user}:{password}@{ip}:{port}/11"
cap = cv2.VideoCapture(url)  # Activating the VideoCapture class in the specific url

class VideoShow(ft.UserControl):
    def __init__(self):
        super().__init__()

    def did_mount(self):
        self.video_update()

    def video_update(self):
        while True:
            try:
                _, frame = cap.read()  # Getting a image frame of IP camera
                frame = cv2.resize(frame, (550,350), cv2.INTER_AREA) # Controlling the image size
                _, img_arr = cv2.imencode(".png", frame)             # Generating the array data from image frame
                img_b64 = base64.b64encode(img_arr)                  # Converting the array data into base64 type for web
                self.img.src_base64 = img_b64.decode("utf-8")        # Generating the image path from image data based on base64
                self.update()
            except Exception as e:    # for passing the error coming from no image data before starting
                print(e)
                break
    
    def build(self):
        self.img = ft.Image(border_radius = ft.border_radius.all(10))
        return self.img

def main(page: ft.Page):
    page.window_width = 800
    page.window_height = 650
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

    left_sec = ft.NavigationRail(
        selected_index = 0,
        label_type = ft.NavigationRailLabelType.ALL,
        min_width = 140,
        min_extended_width = 200,
        leading = ft.FloatingActionButton(
            content = ft.Row(
                [
                    ft.Icon(ft.icons.ADD),
                    ft.Text("FIRST")
                ],
                alignment = "center"
            ),
            bgcolor = ft.colors.AMBER_300,
            shape = ft.RoundedRectangleBorder(radius = 5),
            width = 90,
            mini = True,
        ),
        group_alignment = -0.7,
        destinations = [
            ft.NavigationRailDestination(
                icon = ft.icons.ADD_OUTLINED,
                selected_icon_content = ft.Icon(ft.icons.ADD),
                label_content = ft.Text("SECOND") ),
            ft.NavigationRailDestination(
                icon_content = ft.Icon(ft.icons.BOOKMARK_BORDER),
                selected_icon_content = ft.Icon(ft.icons.BOOKMARK),
                label_content = ft.Text('THIRD') ),
            ft.NavigationRailDestination(
                icon = ft.icons.SETTINGS_OUTLINED,
                selected_icon_content = ft.Icon(ft.icons.SETTINGS),
                label_content = ft.Text("SETTINGS") )
        ],
        # on_change = lambda e: print('Selected Destination: ',
        #                             e.control.selected_index )
    )

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
                                VideoShow(),
                                ft.Text(
                                    "   Now, Camera Is Running In Real Time..",
                                    size = 15,
                                    color = ft.colors.BLACK,
                                    weight = ft.FontWeight.BOLD,
                                    italic = True,
                                    style = ft.TextThemeStyle.TITLE_MEDIUM
                                ),
                                
                            ]
                        )
                    )
                ),
                ft.Text("| Camera Name : IPCAM",
                        size = 14,
                        weight = ft.FontWeight.BOLD,
                        italic = True ),
                ft.Text("| User Name : homecam",
                        size = 14,
                        weight = ft.FontWeight.BOLD,
                        italic = True ),
                ft.Text(f"| Recent Public IP : {ip}:{port}",
                        size = 14,
                        weight = ft.FontWeight.BOLD,
                        italic = True )
            ],
            alignment = ft.MainAxisAlignment.CENTER,
            expand = True
        )
    )

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
    page.add(section_all)
    page.update()

if __name__ == "__main__":
    ft.app(target = main)
    cap.release()
    cv2.destroyAllWindows()

