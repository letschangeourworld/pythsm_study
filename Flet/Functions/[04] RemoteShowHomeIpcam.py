
'''
[Basic Functions Reference]
□ page     : - Whole page of window
             - padding,window_width,window_height,appbar,
               theme_mode,scroll,add,update
                ---> ft.Page(), flet 클래스
□ usercontrol : controlling the Funtions inside a Class through a build function
                ---> ft.UserControl, flet 클래스
□ controls : A list of Controls to display inside the Row,Column,Stack
                ---> flet클래스 내부 인수, list 데이터 받음 
□ append   : adding the data to the list repeatedly (python 내장함수)
□ stack    : - Lists laying a Container upon another
             - width,height,bgcolor,border_radius,...
                ---> ft.Stack(). flet 클래스, list 데이터 받음 
□ Container : - A outer frame inside a window page
              - content,margin,padding,alignment,width,height,border_radius,
                bottom,gradient,ink,on_click,animate,...                         
                ---> ft.Container(), flet 클래스
                ---> ft.border_radius(), flet 함수
                ---> ft.padding(), flet 함수 
                ---> ft.margin(), flet 함수
□ gradient : - Displaying and merging with the various colors on the specific background
             - LinearGradient(begin,end,colors)
                ---> ft.LinearGradient(), flet 함수
                ---> ft.alignment(), flet 함수 
□ content  : Column([Text, Row],spacing,scroll),
             Image(src,width,height,border_radius,fit)
                ---> ft.Column(), flet 클래스
                ---> ft.Image(), flet 클래스
                ---> ft.border_radius, flet 함수
                ---> ft.ImageFit, flet 클래스
□ Text     : (value,weight,size,color,style,..)
                ---> ft.Text(), flet 클래스
                     └> value : string type
                     └> ft.FontWeight()
                     └> ft.TextThemeStyle()
□ Row      : - Arranging in the direction of row for components
             - controls,spacing,alignment
                ---> ft.Row(), flet 클래스, list 데이터 받음 
                     └> ft.MainAxisAlignment()
□ Column   : - Arranging in the direction of column for components
             - controls,alignment,horizontal_alignmnet,wrap,width,height,
               spacing,run_spacing,scroll,on_scroll,on_scroll_interval,... 
                ---> ft.Column(), flet 클래스, list 데이터 받음
                     └> ft.ScrollMode()
□ AppBar   : - The design at the top of window page
             - AppBar(leading,leading_width,title,bgcolor,...)
                ---> ft.AppBar(), flet 클래스
                ---> ft.Icon(), flet 클래스
                      └> ft.icons(), flet 함수
                      └> ft.colors(), flet 함수
□ NavigationRail : - The menu for importing or exporting an another functions or pages
                   - selected_index,label_type,min_width,min_extended_width,
                     leading,group_alignment,destinations,on_change,on_click,...
                     ---> ft.NavigationRailLabelType()
                     ---> ft.NavigationRailDestination()
□ FloatingActionButton : - Action Button
                         - content,bgcolor,shape,width,on_click,on_change,...
'''
####################################################################
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
        self.img = ft.Image(border_radius = ft.border_radius.all(10))  # Cover ft.Image class onto self.imag path
        return self.img

def main(page: ft.Page):
    # Control the size of Window page
    page.window_width = 800
    page.window_height = 650
    
    # Appbar at the top of window page
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

    # For the Functions at the Left part of page
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
    
    # For the Functions at the Right part of page
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
                ft.Text(f"| User Name : {user}",
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

    # For merging with 2 parts of page
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

