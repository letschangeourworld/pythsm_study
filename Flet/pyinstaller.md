
사용조건
1. python 3.6 이상 버전
2. Windows 8 이상, Mac OS X 10.7 이상, Linux
3. 각 운영체제에서 compile된 실행파일은 그 운영체제에서만 사용가능

사용진행과정
1. pip install pyinstaller
2. pyinstaller --version
3. pip install --upgrade pyinstaller
4. 명령프롬프트에서 pyinstaller aaa.py 로 실행
5. 해당폴더에 다음 폴더와 파일 생성됨
     - folders : build, dist
     - file : aaa.spec
6. dist 폴더 내에 aaa.exe 실행파일 찾을 수 있음
7. 실행파일 외에 다른 dll 파일들이 많이 생성되어 있어 모아주는 옵션 실행
     - pyinstaller -F aaa.py
     - pyinstaller -w  or pyinstaller -noconsole : 실행파일 실행시 콘솔창이 뜨는 경우에 사용 (요즘엔 안 뜸)
8. dist 폴더 내에 실행파일 1개만 보임

※ multiprocessing 모듈 사용하는 프로그램이라면 main 구문에 freez_support() 추가해야 함

  
