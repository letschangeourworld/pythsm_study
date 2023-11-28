
사용조건
1. python 3.6 이상 버전
2. Windows 8 이상, Mac OS X 10.7 이상, Linux
3. 각 운영체제에서 compile된 실행파일은 그 운영체제에서만 사용가능

사용법
1. 설치 : pip install pyinstaller
2. 버전확인 : pyinstaller --version
3. 버전업그레이드 : pip install --upgrade pyinstaller
4. 기본 실행 방법 : 명령프롬프트에서 pyinstaller aaa.py 로 실행 (aaa.py는 현재폴더로 리렉토리 주소를 모두 적어줘도 됨)
5. 해당폴더에 다음 폴더와 파일 생성됨
     - folders : build, dist
     - file : aaa.spec
6. dist 폴더 내에 aaa.exe 실행파일 찾을 수 있음
7. 실행파일 1개로 실행방법 : 실행파일 외에 다른 dll 파일들이 많이 있어 모아주는 옵션 (사용시 실행속도가 느릴 수 있음)
     - pyinstaller -F aaa.py
     - pyinstaller -w  or pyinstaller -noconsole : 실행파일 실행시 콘솔창이 뜨는 경우에 사용 (요즘엔 안 뜸)
        → 프롬프트에서 pyinstaller -w -F aaa.py 과 같이 입력실행
8. 이름지정방법
     - -n NAME 으로 실행 → pyinstaller -w -F -n beautifulApp.exe
     - 맨 위에서 기본실행시 파일이름은 aaa로 됨
9. 아이콘 설정방법 : 탐색창에서 보여지는 아이콘 설정하는 방법
     - pyinstaller -w -F --icon=img.ico aaa.py  (이미지 아이콘 파일명 : img.ico)
     - ico확장자도 제공해주는 이미지 사이트에서 다운로드하면 됨
     - 이미지 확장명이 png, jpg 이라면, ico 확장자로 변환해줘야 함 (인터넷에서 변환해주는 프로그램 있음)

※ multiprocessing 모듈 사용하는 프로그램이라면 main 구문에 freez_support() 추가해야 함

  
