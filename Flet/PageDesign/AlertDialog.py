import flet as ft

def main(page: ft.Page):
    page.title = 'Alert Window'

    # Dialog 기본 정의 : 기본 형태 활성화 -> 변수저장
    dlg = ft.AlertDialog(title = ft.Text('Check machines!'),
                         on_dismiss = lambda e: print('Dialog dismissed!')
                         )
    
    # 초기상태 : 구조 형태 비활성 상태
    def close_dlg(e):
        dlg_modal.open = False
        page.update()

    # Dialog 구조 형태 정의 : 구조 형태 활성화 -> 변수저장
    dlg_modal = ft.AlertDialog(
        modal = True,
        title = ft.Text('Please check out'),
        content = ft.Text('Do you really want to remove all files?'),
        actions = [
            ft.TextButton('Yes', on_click = close_dlg),
            ft.TextButton('No', on_click = close_dlg),
        ],
        actions_alignment = ft.MainAxisAlignment.END,
        on_dismiss = lambda e: print('Modal dialog dismissed!')
    )
    
    # Dialog 기본형태 page에 반영후 활성화
    def open_dlg(e):
        page.dialog = dlg
        dlg.open = True
        page.update()

    # Dialog 구조형태 page에 반영후 활성화
    def open_dlg_modal(e):
        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()

    # page에 버튼 생성
    page.add(
        ft.ElevatedButton('Open Dialog', on_click = open_dlg),
        ft.ElevatedButton('Open Modal Dialog', on_click = open_dlg_modal)
    )

ft.app(target = main)

