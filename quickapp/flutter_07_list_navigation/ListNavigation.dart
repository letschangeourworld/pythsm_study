
import 'package:flutter/material.dart';
import 'package:scoped_model/scoped_model.dart';

class Product extends Model {
  final String name;
  final String description;
  final int price;
  final String image;
  int rating;

  Product(this.name, this.description, this.price, this.image, this.rating);

  factory Product.fromMap(Map<String,dynamic> json) {
    return Product(
      json['name'],
      json['decription'],
      json['price'],
      json['image'],
      json['rating'],
    );
  }
  void updateRating(int myRating) {
    rating = myRating;
    notifyListeners();
  }

  static List<Product> getProducts() {
    List<Product> items = <Product>[];

    items.add(Product(
      'iPhone',
      'iPhone is the stylist phone ever.',
      1000,
      'iphone.jpg',
      0 ));

    items.add(Product(
      'Laptop',
      'Laptop is most useful device.',
      2000,
      'iphone.jpg',
      0 ));

    return items;
  }
}

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'AnyLike',
      theme: ThemeData(
        primarySwatch: Colors.blueGrey,
      ),
      home: MyHomePage(title:'AnyLike'),
    );
  }
}

class MyHomePage extends StatelessWidget {
  MyHomePage({Key? key, required this.title}) : super(key: key);

  final String title;
  final items = Product.getProducts();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AnyLike Product Navigation'),
      ),
      body: ListView.builder(
        itemCount: items.length,
        itemBuilder: (context, index) {
          return ProductBox(item: items[index]);
        },
      )
    );
  }
}

class RatingBox extends StatelessWidget {
  const RatingBox({Key? key, required this.item}) : super(key: key);

  final Product item;

  @override
  Widget build(BuildContext context) {
    double size = 25;
    return Row(
      mainAxisAlignment: MainAxisAlignment.end,
      crossAxisAlignment: CrossAxisAlignment.end,
      mainAxisSize: MainAxisSize.min,
      children: <Widget>[
        Container(
          padding: const EdgeInsets.all(0),
          child: IconButton(
            icon: (item.rating >= 1 ? Icon(Icons.star,size: size):
            Icon(Icons.star_border,size: size)),
            color: Colors.blue[500],
            onPressed: () => item.updateRating(1),
            iconSize: size,
          ),
        ),
        Container(
          padding: const EdgeInsets.all(0),
          child: IconButton(
            icon: (item.rating >= 2 ? Icon(Icons.star, size: size):
            Icon(Icons.star_border, size: size)),
            color: Colors.blue[500],
            onPressed: () => item.updateRating(2),
            iconSize: size,
          ),
        ),
        Container(
          padding: const EdgeInsets.all(0),
          child: IconButton(
            icon: (item.rating >= 3 ? Icon(Icons.star, size: size):
            Icon(Icons.star_border, size: size)),
            color: Colors.blue[500],
            onPressed: () => item.updateRating(3),
            iconSize: size,
          ),
        ),
      ],
    );
  }
}

class ProductBox extends StatelessWidget {
  const ProductBox({Key? key, required this.item}) : super(key: key);

  final Product item;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(2),
      height: 140,
      child: Card(
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: <Widget>[
            Image.asset('images/${item.image}',width: 150, height: 140),
            Expanded(
              child: Container(
                padding: const EdgeInsets.all(5),
                child: ScopedModel<Product>(
                  model: item,
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: <Widget>[
                      Text(
                        item.name,
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      Text(item.description),
                      Text(
                        'Price: KRW ${item.price}'
                      ),
                      ScopedModelDescendant<Product>(
                          builder: (context, child, item) {
                            return RatingBox(item: item);
                          }
                      )
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
