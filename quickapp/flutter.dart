
/*
FlutterFlow로 만든 앱 화면을 App Store에 게시하고 
서비스하기 위해서는 Xcode를 사용하여 앱을 빌드해야 합니다. 

1. 우선 Mac OS용 컴퓨터와 Xcode를 설치합니다.
2. FlutterFlow에서 앱을 빌드하기 위해 Flutter SDK를 설치합니다.
3. FlutterFlow에서 에셋을 준비합니다.
4. Xcode에서 새로운 프로젝트를 만듭니다.
5. Flutter 앱을 Xcode 프로젝트에 추가합니다.
6. Flutter 앱의 정보를 업데이트하고 그림자와 텍스트 스타일 등 UI 디자인을 변경합니다.
7. 최종 앱을 빌드합니다.
8. Developer Program의 일부인 앱 스토어 Connect에서 앱을 업로드하고, 검토 및 승인을 받습니다. 

위와 같은 과정을 거쳐 FlutterFlow로 만든 앱 화면을 App Store에서 서비스할 수 있습니다.
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
                  // 입력한 정보를 저장하거나 다른 작업을 수행할 수 있는 코드 작성
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
