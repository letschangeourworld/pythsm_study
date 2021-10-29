Smart Logistics

주요 물류센터에 각종 자동화 기기를 도입하며 ‘스마트 물류’를 실현하고 있다. 
최근에는 자동차 반조립 부품(KD, Knock-Down) 물류기지인 KD센터에 포장 관련 자동화 로봇 개발과 구축을 완료했다. 
기존 수작업으로 진행하던 일부 작업 라인을 자동화 기기로 전환해 생산성을 높이기 위한 시도다. 
기다란 작업 라인에 로봇과 부품이 아래 그림과 같이 단위 간격으로 놓여 있다. 로봇들의 위치에서 거리가 K 이하인 부품만 잡을 수 있다. 왼쪽 오른쪽은 상관 없다.

![image](https://www.softeer.ai/upload/2021/09/20210908_190458029_48765.jpeg)

위 그림에서 K = 1인 경우를 생각해보자. 이 경우 모든 로봇은 그의 위치 바로 옆에 인접한 부품만 집을 수 있다. 
10번 위치에 있는 로봇은 바로 왼쪽 11번 위치에 있는 부품을 집을 수 있다. 
이 경우 다음과 같이 최대 5개의 로봇이 부품을 집을 수 있다. 

* 2번 위치에 있는 로봇은 1번 위치에 있는 부품을 집을 수 있다. <br>
* 4번 위치에 있는 로봇은 5번 위치에 있는 부품을 집을 수 있다. <br>
* 6번 위치에 있는 로봇은 7번 위치에 있는 부품을 집을 수 있다.<br>
* 9번 위치에 있는 로봇은 8번 위치에 있는 부품을 집을 수 있다. <br>
* 10번 위치에 있는 로봇은 11번 위치에 있는 부품을 집을 수 있다.<br>
* 12번 위치에 있는 로봇은 집을 수 있는 부품이 없다. 

만약 K = 2라고 한다면 다음과 같이 6개 로봇 모두가 부품을 집을 수 있다.<br>

* 2번 위치에 있는 로봇은 1번 위치에 있는 부품을 집을 수 있다. <br>
* 4번 위치에 있는 로봇은 3번 위치에 있는 부품을 집을 수 있다. <br>
* 6번 위치에 있는 로봇은 5번 위치에 있는 부품을 집을 수 있다. <br>
* 9번 위치에 있는 로봇은 7번 위치에 있는 부품을 집을 수 있다. <br>
* 10번 위치에 있는 로봇은 8번 위치에 있는 부품을 집을 수 있다. <br>
* 12번 위치에 있는 로봇은 11번 위치에 있는 부품을 집을 수 있다. <br>

라인의 길이 N, 부품을 집을 수 있는 거리 K, 그리고 로봇과 부품의 위치가 주어졌을 때 부품을 집을 수 있는 로봇의 최대 수를 구하는 프로그램을 작성하라.

(입력형식) <br>
입력의 첫 줄에는 두 정수 N과 K가 나온다. <br>
(1 ≤ N ≤ 20,000, 1 ≤ K ≤ 10) <br>
다음 줄에는 로봇과 부품의 위치가 문자 P(로봇)와 H(부품)로 이루어지는 길이 N인 문자열로 주어진다.

(출력형식) <br>
여러분은 첫 줄에 하나의 정수를 출력한다. <br>
이 수는 입력에 대해서 부품을 집을 수 있는 최대 로봇 수를 나타낸다.

(입력예제 1) <br>
20 1 <br>
HHPHPPHHPPHPPPHPHPHP 

(출력예제 1) <br>
8 

(입력예제 2) <br>
20 2 <br>
HHHHHPPPPPHPHPHPHHHP

(출력예제 2) <br>
7