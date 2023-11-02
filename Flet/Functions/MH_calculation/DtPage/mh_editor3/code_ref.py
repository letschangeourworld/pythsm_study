import flet as ft

def code_ref_txt(keys, values):
    return ft.Card(
        ft.Container(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                f"Code {str(value)} : {key}",
                                weight = "bold",
                                font_family = "HDText",
                                text_align = ft.TextAlign.CENTER,
                                size = 13
                            )
                        ]
                    ) for key, value in zip(keys, values)
                ]
            ),
            alignment = ft.MainAxisAlignment.START,
            padding = 25
        ),
        elevation = 5
    )
    
    