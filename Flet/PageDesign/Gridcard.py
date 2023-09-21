import flet as ft
from Moviedata import grid_list_image

gridcom = ft.GridView(
    expand = 3,
    runs_count = 5,
    max_extent = 150,
    child_aspect_ratio = 1,
    spacing = 15,
    run_spacing = 15
    )

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

# To insert the images to Grid
for x in grid_list_image:
    gridcom.controls.append(
        ft.Card(
            elevation = 20,
            content = ft.Image(
                src = x,
                border_radius = ft.border_radius.all(10),
                fit = ft.ImageFit.COVER
                )
            )
        )

gridscreen = ft.Container(
    margin = ft.margin.only(left = 20),
    content = ft.Column(
        [ft.Text('Now Showing',
              weight = 'bold',
              size = 30,
              color = 'white'),
         gridcom],
        scroll = 'auto'
        )
    )
