/*
[flutterflow 따라하기 강의]
   https://m.blog.naver.com/rock11201/222879641299
[flutterflow 사이트]
   https://flutterflow.io/

   https://thoughtful-tarsier-267.notion.site/f408ac46e2c34cd981a1b2e3033aef98

FlutterFlow로 만든 앱 화면을 
App Store에 게시하고 서비스하기 위해서는
Xcode를 사용하여 앱을 빌드해야 한다.

1. 우선 Mac OS용 컴퓨터와 Xcode를 설치
2. FlutterFlow에서 앱을 빌드하기 위해 Flutter SDK를 설치
3. FlutterFlow에서 에셋을 준비
4. Xcode에서 새로운 프로젝트를 만듬
5. Flutter 앱을 Xcode 프로젝트에 추가
6. Flutter 앱의 정보를 업데이트하고 그림자와 텍스트 스타일 등 UI 디자인을 변경
7. 최종 앱을 빌드
8. Developer Program의 일부인 앱 스토어 Connect에서 앱을 업로드하고,
   검토 및 승인을 받음

위와 같은 과정을 거쳐 FlutterFlow로 만든 앱 화면을 
App Store에서 서비스할 수 있슴
*/

import 'package:flutter/material.dart';

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'My App',
      home: Scaffold(
        appBar: AppBar(
          title: Text('My App'),
        ),
        body: Center(
          child: Column(
            children: <Widget>[
              TextField(
                decoration: InputDecoration(
                  labelText: '이름',
                ),
              ),
              TextField(
                decoration: InputDecoration(
                  labelText: '이메일',
                ),
              ),
              ElevatedButton(
                onPressed: () { 
             // 입력정보 저장 또는 다른 작업 수행 가능
                },
                child: Text('저장'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/*
위 코드는 화면 중앙에 이름과 이메일을 입력할 수 있는 두 개의 텍스트 필드와 
입력한 정보를 저장할 수 있는 저장 버튼이 있는 간단한 화면이다.
코드 상에서 `TextField` 위젯을 사용하여 입력 필드를 생성하고 
`ElevatedButton` 위젯을 사용하여 저장 버튼을 생성한다. 버튼 클릭 시,
onPressed 콜백 함수를 통해 입력한 정보를 저장하거나 다른 작업을 수행할 수 있다.
*/

