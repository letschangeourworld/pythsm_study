import flet as ft

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
# Row      : ([list_data],scroll,alignment)

appmenu = ft.Row([
    ft.CircleAvatar(
        foreground_image_url = "https://image2.1004gundam.com/item_images/goods/380/1376395068.jpg"),
    ft.Container(
        margin = ft.margin.symmetric(vertical = 40),
        content = ft.Row([
            ft.Icon(name = 'pin_drop', color = 'white'),
            ft.Text('Seoul City', color = 'white'),
            ft.Icon(name = 'search', color = 'white')
        ])
        )
    ]
    )
