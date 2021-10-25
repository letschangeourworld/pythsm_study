한 두 줄 입력받는 문제들과 다르게, 
반복문으로 여러 줄을 입력 받아야 할 때,
input()으로 입력 받으면 시간초과가 발생할 수 있다.

import sys

T = int(input())   # Test case
for i in range(T):
    a,b = map(int, sys.stdin.readline().split())
    print(a+b)

맨 첫 줄 Test case를 입력받을 때는 input()을 사용해도 무방하다.
그러나 반복문으로 여러줄 입력받는 상황에서는 반드시 
sys.stdin.readline()을 사용해야 시간초과가 발생하지 않는다.

💡 sys.stdin.readline() 사용법
📌한 개의 정수를 입력받을 때

import sys
a = int(sys.stdin.readline())

😨 그냥 a = sys.stdin.readline() 하면 안되나요?
👉 sys.stdin.readline()은 한줄 단위로 입력받기 때문에, 
   개행문자가 같이 입력 받아진다.
   만약 3을 입력했다면, 3\n 이 저장되기 때문에, 개행문자를 제거해야 한다.
   또한, 변수 타입이 문자열 형태(str)로 저장되기 때문에, 
   정수로 사용하기 위해서 형변환을 거쳐야 한다.

📌정해진 개수의 정수를 한 줄에 입력받을 때

import sys
a,b,c = map(int,sys.stdin.readline().split())

map()은 반복 가능한 객체(리스트 등)에 대해 각각의 요소들을 지정된 함수로 처리해주는 함수이다.
위와 같이 사용한다면 a,b,c에 대해 각각 int형으로 형변환을 할 수 있다.

📌 임의의 개수의 정수를 한줄에 입력받아 리스트에 저장할 때

import sys
data = list(map(int,sys.stdin.readline().split()))

split()은 문자열을 나눠주는 함수이다.
괄호 안에 특정 값을 넣어주면 그 값을 기준으로 문자열을 나누고, 
아무 값도 넣어주지 않으면 공백(스페이스, 탭, 엔터 등)을 기준으로 나눈다.

list()는 자료형을 리스트형으로 변환해주는 함수이다.
map()은 맵 객체를 만들기 때문에, 리스트형으로 바꿔주기 위해서 list()로 감싸 주었다.

📌 임의의 개수의 정수를 n줄 입력받아 2차원 리스트에 저장할 때

import sys
data = []
n = int(sys.stdin.readline())
for i in range(n):
    data.append(list(map(int,sys.stdin.readline().split())))

이렇게 한다면 각 요소의 길이가 동일한 2차원 리스트도 만들 수 있고,
각각 길이가 다른 2차원 리스트도 입력 받을 수 있다.

📌 문자열 n줄을 입력받아 리스트에 저장할 때

import sys
n = int(sys.stdin.readline())
data = [sys.stdin.readline().strip() for i in range(n)]

strip()은 문자열 맨 앞과 맨 끝의 공백문자를 제거한다.
