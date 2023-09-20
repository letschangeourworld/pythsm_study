import flet as ft

# 채팅 메시지의 기본 구성 재료 : 채팅하는사람이름, 채팅 메시지, 채팅 메시지의 종류(타입)
class Message():
    def __init__(self, user_name: str, text: str, message_type: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type

# 채팅 메시지 : 채팅메시지는 메시지가 행(Row)으로 입력되면서 열(Column)로 채워진다.
# 또한 한 개의 메시지 행 내에서도 열로 구분된다. 
# 예를들면, 행 안에 맨 좌측에 이름이 적히고, 그 옆에 메시지가 적힌다.

class ChatMessage(ft.Row):
    # 메시지행 기본 구조 초기화
    def __init__(self, message: Message):
        super().__init__()                # 상위클래스 초기화 조건 모두 상속
        self.vertical_alignment = "start" # 수직 방향 배열
        # controls : 어떤 행위를 만듬, 리스트 타입 입력
        # 아바타 아이콘 생성, 채팅란 (이름 아래 메시지로 수직배열)
        self.controls = [
            ft.CircleAvatar(
                content = ft.Text( self.get_initials(message.user_name) ), # 아바타 안에 채팅자 이름 초성글자 넣기
                color = ft.colors.WHITE,                                   # 글자 흰색 설정
                bgcolor = self.get_avatar_color(message.user_name)         # 아바타아이콘 배경색 설정
                ),
            ft.Column(
                [ft.Text(message.user_name, weight = "bold"),   # 채팅자이름 굵은글씨설정
                 ft.Text(message.text, selectable = True)],     # 채팅 텍스트
                tight = True,                                   # 꽉 채워서 배열
                spacing = 5                                     # 주변과의 거리설정
                )
            ]
    
    # 아바타 아이콘 안에 채팅자 이름의 초성 대문자 가져오기
    def get_initials(self, user_name: str):
        return user_name[:1].capitalize()

    # 아바타 아이콘 칼라 랜덤하게 설정
    def get_avatar_color(self, user_name: str):
        colors_lookup = [
            ft.colors.AMBER,
            ft.colors.BLUE,
            ft.colors.BROWN,
            ft.colors.CYAN,
            ft.colors.GREEN,
            ft.colors.INDIGO,
            ft.colors.LIME,
            ft.colors.ORANGE,
            ft.colors.PINK,
            ft.colors.PURPLE,
            ft.colors.RED,
            ft.colors.TEAL,
            ft.colors.YELLOW
            ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]

# 실행용 Main 메서드
def main(page: ft.Page):
    page.horizontal_alignment = "stretch"  # 채팅창의 기본배열방향 : 수평
    page.title = "Flet Chat Window"        # 채팅창 이름설정

    # 채팅참여클릭 메서드 (로그인창)
    def join_chat_click(e):
        # 채팅자 이름입력값이 없을 경우, 에러문 생성
        if not join_user_name.value:
            join_user_name.error_text = "Name cannot be blank!"  # 이름입력란에 에러메시지를 넣기
            join_user_name.update()  # 그 상태로 업데이트
        else:
            page.session.set("user_name", join_user_name.value)  # 이름값 입력받으면 채팅세션가동
            page.dialog.open = False                             # 이름값 입력창 닫기
            page.dialog.modal = False                            # 이름값 입력창 닫기
            new_message.prefix = ft.Text(f"{join_user_name.value}: ") # 채팅입력란에 '이름 :'과 같이 입력하고 대기
            # 현재 채팅창 구독 시작하면서 채팅자가 들어왔다는 메시지 전송
            # 메시지 타입은 '로그인 메시지'
            page.pubsub.send_all(
                Message(user_name = join_user_name.value,
                        text = f"{join_user_name.value} has joined the chat.",
                        message_type = "login_message")
                        )
            page.update()  # 그 상태로 업데이트
    
    # 메시지란 입력후 클릭 메서드 (채팅창)
    def send_message_click(e):
        # 새메시지가 입력되었을 경우에만 실행
        if new_message.value != "":
            # 현재 채팅창 구독 시작하면서 새 메시지 전송
            # 메시지 타입은 '채팅 메시지'
            page.pubsub.send_all(
                Message(page.session.get("user_name"),
                        new_message.value,
                        message_type = "chat_message")
                        )
            new_message.value = ""
            new_message.focus()
            page.update()
    
    def on_message(message: Message):
        if message.message_type == "chat_message":
            m = ChatMessage(message)
        elif message.message_type == "login_message":
            m = ft.Text(message.text,
                        italic = True,
                        color = ft.colors.BLACK45,
                        size = 12)
        chat.controls.append(m)
        page.update()
    
    page.pubsub.subscribe(on_message)
    
    # A dialog asking for a user display name
    join_user_name = ft.TextField(label = "Enter your name to join the chat",
                                  autofocus = True,
                                  on_submit = join_chat_click
                                  )
    
    page.dialog = ft.AlertDialog(open = True,
                                 modal = True,
                               title = ft.Text("Welcome!"),
                               content = ft.Column([join_user_name],
                                                     width = 200,
                                                     height = 60,
                                                     tight = True
                                                      ),
                                actions = [ft.TextButton(text = "Join chat",
                                                         on_click = join_chat_click)],
                                actions_alignment = "end"
                                )
    
    # Chat messages
    chat = ft.ListView(
        expand = True,
        spacing = 10,
        auto_scroll = True
        )
    
    # A new message entry form
    new_message = ft.TextField(
        hint_text = "Write a message...",
        autofocus = True,
        shift_enter = True,
        min_lines = 1,
        max_lines = 5,
        filled = True,
        expand = True,
        on_submit = send_message_click
        )
    
    # Add everything to the page
    page.add(ft.Container(
        content = chat,
        border = ft.border.all(1, ft.colors.OUTLINE),
        border_radius = 5,
        padding = 10,
        expand = True
        ),

        ft.Row([new_message,
                ft.IconButton(
                    icon = ft.icons.SEND_ROUNDED,
                    tooltip = "Send message",
                    on_click = send_message_click)
                    ])
                    )

ft.app(target = main, view = ft.WEB_BROWSER)
