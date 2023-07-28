
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
        primarySwatch: Colors.blue,
      ),
      home: const MyHomePage(title:'AnyLike'),
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
        title: const Text('Product Listing'),
      ),
      body: ListView(
        shrinkWrap: false,
        padding: const EdgeInsets.all(0),
        children: const <Widget>[
          ProductBox(
            name: 'IPhone',
            description: 'iPhone is the stylist phone ever.',
            price: 1000,
            image: 'IPhone.jpg',
          ),
          ProductBox(
            name: 'Laptop',
            description: 'Laptop is most productive development tool.',
            price: 2000,
            image: 'IPhone.jpg'
          ),
          ProductBox(
            name: 'Pen_drive',
            description: 'Pen_drive is the stylish ever.',
            price: 100,
            image: 'IPhone.jpg',
          ),
          ProductBox(
            name: 'Tablet_PC',
            description: 'Tablet PC is the most useful device for meeting.',
            price: 1000,
            image: 'IPhone.jpg',
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
        required this.image }) : super(key: key);

  final String name;
  final String description;
  final int price;
  final String image;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(1),
      height: 140,
      child: Card(
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: <Widget>[
            Image.asset(image),
            Expanded(
              child: Container(
                padding: const EdgeInsets.all(0),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: <Widget>[
                    Text(
                      name,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    Text(description),
                    Text('Price: $price USD'),
                  ],
                ),
              ),
            ),
          ],
        ),
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
    double size = 10;
    // print(_rating);
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceAround,
      crossAxisAlignment: CrossAxisAlignment.center,
      mainAxisSize: MainAxisSize.max,
      children: <Widget>[
        Container(
          padding: const EdgeInsets.all(0),
          child: IconButton(
            icon: (_rating >= 1 ? Icon(Icons.star, size: size,) :
            Icon(Icons.star_border, size: size,)),
            color: Colors.red[500],
            onPressed: _setRatingAsOne,
            iconSize: size,
          ),
        ),
        Container(
          padding: const EdgeInsets.all(0),
          child: IconButton(
            icon: (_rating >= 2 ? Icon(Icons.star, size: size,) :
            Icon(Icons.star_border, size: size,)),
            color: Colors.red[500],
            onPressed: _setRatingAsTwo,
            iconSize: size,
          ),
        ),
        Container(
          padding: const EdgeInsets.all(0),
          child: IconButton(
            icon: (_rating >= 3 ? Icon(Icons.star, size: size,) :
            Icon(Icons.star_border, size: size,)),
            color: Colors.red[500],
            onPressed: _setRatingAsThree,
            iconSize: size,
          ),
        ),
      ],
    );
  }
}
