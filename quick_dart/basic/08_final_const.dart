// final and const

void main() {
  final String firstName = 'pythsm';
  const String lastName = 'Dev';
  print(firstName);
  print(lastName);

  final DateTime now1 = DateTime.now();
  print(now1);

  // ERROR
  // const DateTime now2 = DateTime.now();
  // print(now2);
}
