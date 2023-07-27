/*
| Structure |
 Container <- Card <- Row <-
 Row <- 1. Image
        2. Expanded <- Container <- Column <- Text1 / Text2 / Text3
*/

import 'package:flutter/material.dart';

void main() => runApp(const MyApp()); // const

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);  // null check for Key

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,  // remove upper banner
      title: 'AnyLike',  // title of window
      theme: ThemeData(
        primarySwatch: Colors.cyan, // appbar color
      ), // ThemData
      home: const MyHomePage(), // const
    ); // MaterialApp
  }
}

class MyHomePage extends StatelessWidget {
  const MyHomePage({Key? key, this.title}) : super(key: key); // null check for Key
  
  final String? title; // null check
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("AnyLike Product")), // const
      body: ListView(
        shrinkWrap: true,
        padding: const EdgeInsets.fromLTRB(2.0, 10.0, 2.0, 10.0), // const
        children: const <Widget>[ // const, Widget <- W UpperLetter
          ProductBox(
            name: 'iPhone',
            price: 1000,
            image: "iphone.jpg"
          ), // ProductBox
        ], // <Widget>[]
      ), // ListView
    ); // Scaffold
  }
}

class ProductBox extends StatelessWidget {
  // null check : ? and required
  const ProductBox({Key? key, this.name, this.price, required this.image}) : super(key: key);
  final String? name; // null check
  final int? price; // null check
  final String image;
  
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(2), // const
      height: 120,
      child: Card(
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: <Widget>[
            Image.asset('productImage/$image'),
            Expanded(child: Container(
              padding: const EdgeInsets.all(5), // const
              child: Column(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: <Widget>[
                  Text(
                      name!, // null check operator
                  style: const TextStyle(fontWeight: FontWeight.bold) // const
                  ),
                Text("Price: $price USD"),
                ], // <Widget>[]
              ) // Column
            ) // Container
           ) // Expanded
          ], // <Widget>[]
        ), // Row
      ), // Card
    ); // Container
  }
}

/*
| image download site : https://1000logos.net/wp-content/uploads/2017/02/Symbol-of-the-iPhone-logo.jpg
| project folder에 assets/productImage directory 생성후 저장
| pubspec.yaml에 아래 image path 입력후 pub get, pub upgrade
| pubspec.yaml
     assets:
       - productImage/iphone.jpg
*/
