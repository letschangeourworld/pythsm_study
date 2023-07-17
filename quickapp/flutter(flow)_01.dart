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
