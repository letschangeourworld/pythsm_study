import flet as ft
from Moviedata import movie_data

listmovie = ft.Row()
    
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

for x in movie_data:
    listmovie.controls.append(
        ft.Stack([
            ft.Container(
                width = 240,
                height = 170,
                border_radius = ft.border_radius.all(30),
                content = ft.Image(
                    # image rendering
                    src = x['image'],
                    width = 300,
                    height = 270,
                    border_radius = ft.border_radius.all(30),
                    fit = ft.ImageFit.COVER
                    )
                ),
            # Title and Description for image
            ft.Container(
                width = 240,
                padding = ft.padding.only(left = 10),
                gradient = ft.LinearGradient(
                    begin = ft.alignment.bottom_center,
                    end = ft.alignment.top_center,
                    colors = ['black','#48']  # 48 : trasparent
                    ),
                bottom = 10,
                content = ft.Column(
                    [ft.Text(x['title'],
                          weight = 'bold',
                          size = 18,
                          color = 'white'),
                     ft.Text('Now Showing',
                          size = 12,
                          color = 'white')
                    ], spacing = 0
                )
                )
            ])
        )

section2 = ft.Container(
    margin = ft.margin.only(left = 20),
    content = ft.Column([
        ft.Text('For Your Movies',
             weight = 'bold',
             size = 25,
             color = 'white'),
        ft.Row([listmovie],scroll = 'always')
        ], spacing = 1
        )
    )
