// List

void main() {
  List<String> fruits1 = [];

  fruits1.add('Apple');
  fruits1.add('Banana');
  fruits1.add('Kiwi');

  print(fruits1);
  fruits1.removeAt(1);
  print(fruits1);

  List<String> fruits2 = ['Apple', 'Banana', 'Kiwi'];
  print(fruits2);

  List<String> fruits3 = List.from(['Apple', 'Banana', 'Kiwi']);
  print(fruits3);

  List<String> fruits4 = List.filled(3, '');

  fruits4[0] = 'Apple';
  fruits4[1] = 'Banana';
  fruits4[2] = 'Kiwi';

  print(fruits4);

  // 빈 리스트 생성, growable : true 시, 성분을 추가할 때마다 메모리 할당
  // growable : false 시, 성분 추가하려고 해도 안 됨, error 발생
  List<String> fruits5 = List.empty(growable: true);

  fruits5.add('Apple');
  fruits5.add('Banana');
  fruits5.add('Kiwi');

  print(fruits5);

  // 리스트의 각 성분들을 ', '를 중심으로 한 문자열로 연결
  List<String> fruits6 = ['Apple', 'Banana', 'Kiwi'];
  print(fruits6.join(', '));

  List<String> fruits7 = ['Apple', 'Banana', 'Kiwi'];
  print(fruits7.indexOf('Banana')); // 결과 : 1
  print(fruits7.indexOf('Apple')); // 결과 : 0
  print(fruits7.indexOf('Kiwi'));  // 결과 : -1 ==> 리스트의 맨 마지막 성분 의미
  // 리스트 안에 원하는 성분이 존재하지 않아도 -1 를 출력
  print(fruits7.indexOf('a')); // 결과 : -1

  // where() 구문 안에 함수형태로 넣어서 반복 출력
  // indexOf() : 각 문자열에 특정 문자가 포함되어 있는 경우, 그 index 추출
  List<String> fruits8 = ['Apple', 'Banana', 'Kiwi'];
  print(fruits8.where((fruit) => fruit.toLowerCase().indexOf('a') >= 0));

  List<String> fruits9 = ['Apple', 'Banana', 'Kiwi'];

  // 리스트에 있는 내용을 한 개씩 반복 출력
  fruits9.forEach((fruit) {
    print('${fruit}!');
  });

  // 리스트 각각의 요소가 문자열이면 interpolation {} 을 생략해도 됨
  // fruits9.forEach((fruit) {
  //   print('$fruit!');
  // });
  
  for (String fruit in fruits9) {
    print('${fruit}!!');
  }

  // interpolation 생략해도 됨
  // for (String fruit in fruits9) {
  //   print('$fruit!!');
  // }
  
  List<String> fruits10 = ['Apple', 'Banana', 'Kiwi'];
  Iterable<String> newFruits = fruits10.map((e) {
    return 'My name is ${e}';
  });
  print(newFruits);
  print(newFruits.toList());

  // map 함수 안에 함수형태로 입력시키고 Iterable로 반복 입력
  Iterable<String> newFruits1 = fruits10.map((e) => 'My name is $e.');
  print(newFruits);
  print(newFruits.toList());

  /*
  결과
  (My name is Apple, My name is Banana, My name is Kiwi)
  [My name is Apple, My name is Banana, My name is Kiwi]
  (your name is Apple., your name is Banana., your name is Kiwi.)
  [your name is Apple., your name is Banana., your name is Kiwi.]
  */

   
  List<int> numbers1 = [1, 2, 3, 4, 5];
  int result = numbers1.fold(0, (previousValue, element) {
    int sum = previousValue + element;
    return sum * 2;
  });
  print(result);

  List<int> numbers2 = [1, 2, 3, 4, 5];
  int total = numbers2.reduce((value, element) => value + element);
  print(total);

  List<int> numbers3 = [10, 20, 30, 40, 50];
  Iterable indexNumbers = numbers3.asMap().entries.map((e) {
    return 'index: ${e.key} / value: ${e.value}';
  });
  print(indexNumbers);
  print(indexNumbers.toList());
}
