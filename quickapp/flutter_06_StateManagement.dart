/*
1. RatingBox 위젯 : StatefulWidget (State Management)
2. images 폴더생성 > image 저장 > pubspec.yaml > assets 설정
3. MyApp, MyHomePage, ProductBox 위젯 : StatelessWidget
*/

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
        primarySwatch: Colors.indigo,
      ),
      home: const MyHomePage(title:' '),
    );
  }
}

class MyHomePage extends StatelessWidget {
  const MyHomePage({Key? key, required this.title}) : super(key: key);

  final String title;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Product List'),
      ),
      body: ListView(
        shrinkWrap: false,
        padding: const EdgeInsets.all(0),
        children: const <Widget>[
          ProductBox(
            name: 'IPhone',
            description: 'IPhone is the stylist phone ever.',
            price: 1000,
            image: 'iphone.jpg',
          ),
        ],
      ),
    );
  }
}

class ProductBox extends StatelessWidget {
  const ProductBox(
      {Key? key,
        required this.name,
        required this.description,
        required this.price,
        required this.image } ) : super(key: key);

  final String name;
  final String description;
  final int price;
  final String image;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(0),
      height: 140,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: <Widget>[
          Image.asset('images/$image',width: 150, height: 140),
          Expanded(
              child: Container(
                padding: const EdgeInsets.all(0),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: <Widget>[
                    Text(
                      name,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    Text(description),
                    Text('Price : USD $price'),
                    const RatingBox(),
                  ],
                ),
              ),
          ),
        ],
      ),
    );
  }
}

class RatingBox extends StatefulWidget {
  const RatingBox({Key? key}) : super(key: key);
  @override
  RatingBoxState createState() => RatingBoxState();
}

class RatingBoxState extends State<RatingBox> {
  int _rating = 0;
  void _setRatingAsOne() {
    setState(() {
      _rating = 1;
    });
  }
  void _setRatingAsTwo() {
    setState(() {
      _rating = 2;
    });
  }
  void _setRatingAsThree() {
    setState(() {
      _rating = 3;
    });
  }

  @override
  Widget build(BuildContext context) {
    double size = 25;
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      crossAxisAlignment: CrossAxisAlignment.center,
      mainAxisSize: MainAxisSize.min,
      children: <Widget>[
        Container(
          padding: const EdgeInsets.all(1),
          child: IconButton(
            icon: ( _rating >= 1 ? Icon(Icons.star, size: size) :
            Icon(Icons.star_border, size: size)),
            color: Colors.red,
            onPressed: _setRatingAsOne,
            iconSize: size,
          ),
        ),
        Container(
          padding: const EdgeInsets.all(1),
          child: IconButton(
            icon: ( _rating >=2 ? Icon(Icons.start, size: size) :
            Icon(Icons.star_border, size: size)),
            color: Colors.red,
            onPressed: _setRatingAsTwo,
          ),
        ),
        Container(
          padding: const EdgeInsets.all(1),
          child: IconButton(
            icon: ( _rating >= 3 ? Icon(Icons.star, size: size) :
            Icon(Icons.star_border, size: size)),
            color: Colors.red,
            onPressed: _setRatingAsThree,
            iconSize: size,
          ),
        ),
      ],
    );
  }
}
