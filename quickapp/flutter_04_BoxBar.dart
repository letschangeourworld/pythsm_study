import 'package:flutter/material.dart';

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'AnyLike',
      theme: ThemeData(
        primarySwatch: Colors.cyan,
      ),
      home: const MyHomePage(title: 'AnyLike Product'),
    );
  }
}

class MyHomePage extends StatelessWidget {
  const MyHomePage({Key? key, this.title}) : super(key: key);

  final String? title;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("AnyLike Products")),
      body: ListView(
        shrinkWrap: true,
        padding: const EdgeInsets.fromLTRB(2.0, 10.0, 2.0, 10.0),
        children: const <Widget>[
          ProductBox(
            name: 'iPhone',
            price: 1000,
            image: "iphone.jpg"
          ),
        ],
      ),
    );
  }
}

class ProductBox extends StatelessWidget {
  const ProductBox({Key? key, this.name, this.price, required this.image}) : super(key: key);
  final String? name;
  final int? price;
  final String image;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(2),
      height: 120,
      child: Card(
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: <Widget>[
            Image.asset('productImage/$image'),
            Expanded(child: Container(
              padding: const EdgeInsets.all(5),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: <Widget>[
                  Text(
                      name!,
                  style: const TextStyle(fontWeight: FontWeight.bold)
                  ),
                Text("Price: $price USD"),
                ],
              )
            )
           )
          ],
        ),
      ),
    );
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
