import flet as ft
from Moviedata import movie_data

# To deliver the movie data into the specific functions
# controls : controlling the data
# append   : adding the data to the list repeatedly
# stack    : laying a Container upon another
# Container : margin,width,height,border_radius,padding,bottom
#             gradient,content
# gradient : LinearGradient(begin,end,colors)
# content  : Column([Text, Row],spacing,scroll),
#            Image(src,width,height,border_radius,fit)
# Text     : (text_data,weight,size,color)
# Row      : ([list_data],scroll)

# listmovie라는 Row 형태의 빈 list틀 생성
listmovie = ft.Row()

# listmovie 안에 연속으로 Stack 안에 Container 쌓기
# Container 안에 연속으로 이미지 넣기
# 이미지가 없는 Container는 그 안에 Column을 넣기
for x in movie_data:
    listmovie.controls.append(
        ft.Stack(
            [ft.Container(width = 240,
                          height = 170,
                          border_radius = ft.border_radius.all(30),
                          content = ft.Image(
                              src = x['image'],
                              width = 300,
                              height = 270,
                              border_radius = ft.border_radius.all(30),
                              fit = ft.ImageFit.COVER
                              )
                          ),
             
             ft.Container(width = 240,
                          padding = ft.padding.only(left = 10),
                          gradient = ft.LinearGradient(
                              begin = ft.alignment.bottom_center,
                              end = ft.alignment.top_center,
                              colors = ['black','#48'] ),
                          bottom = 10,
                          content = ft.Column(
                              [ft.Text(
                                  x['title'],
                                  weight = 'bold',
                                  size = 18,
                                  color = 'white'),
                               ft.Text('Now Showing',
                                       size = 12,
                                       color = 'white')
                               ],
                              spacing = 0
                              )
                          )
             ]
        )
        )

# 전체 Container 생성
# 전체 Container 안에 Column 삽입
# Column 안에 Text를 넣고 그 아래 Row 삽입
# Row 안에 listmovie 삽입
section2 = ft.Container(margin = ft.margin.only(left = 20),
                        content = ft.Column(
                            [ft.Text('For Your Movies',
                                     weight = 'bold',
                                     size = 25,
                                     color = 'white'),
                             ft.Row([listmovie],
                                    scroll = 'always')
                             ],
                            spacing = 1 )
                        )
