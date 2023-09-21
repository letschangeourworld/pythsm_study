import flet as ft
from Moviedata import grid_list_image

# controls : controlling the data
# append   : adding the data to the list repeatedly
# Card : the fixed form to insert onto the rectangle Grid
# Card : elevation,content
# Container : margin,width,height,border_radius,padding,bottom
#             gradient,content
# gradient : LinearGradient(begin,end,colors)
# content  : Column([Text, Row],spacing,scroll),
#            Image(src,width,height,border_radius,fit)
# Text     : (text_data,weight,size,color)
# Row      : ([list_data],scroll)

# 그리드 틀 만들기
gridcom = ft.GridView(expand = 3,
                      runs_count = 5,
                      max_extent = 150,
                      child_aspect_ratio = 1,
                      spacing = 15,
                      run_spacing = 15
                      )

# 그리드 틀 안에 연속으로 이미지 삽입
# 그리드 틀의 각 칸에 Card 형태로 삽입
# Card 안에 지정된 주소의 이미지를 불러와 이미지 삽입
for x in grid_list_image:
    gridcom.controls.append(
        ft.Card(elevation = 20,
                content = ft.Image(
                    src = x,
                    border_radius = ft.border_radius.all(10),
                    fit = ft.ImageFit.COVER )
                )
        )

# Container 생성
# Container 안에 Column 삽입
# Column 안에 Text 넣고 그 아래 gridcom 삽입
gridscreen = ft.Container(margin = ft.margin.only(left = 20),
                          content = ft.Column(
                              [ft.Text('Now Showing',
                                       weight = 'bold',
                                       size = 30,
                                       color = 'white'
                                      ),
                               gridcom],
                              scroll = 'auto')
                          )
