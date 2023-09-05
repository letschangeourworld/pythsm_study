# server.py : 서버 파일
# streamer.py : 영상디스플레이 파일
# app.py : 실행파일
# 나중에 flask를 WSGI서버에 얹혀서 표현해 볼 예정
# Nginx 웹서버를 사용해서도 표현해 볼 예정

from server import app

version = '0.1.0'

if __name__ == '__main__' :
    print('------------------------------------------------')
    print('CV - version ' + version )
    print('------------------------------------------------')
    app.run(host = '127.0.0.1', port = 5000)
