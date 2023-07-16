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

