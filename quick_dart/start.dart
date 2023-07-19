// 1. 기본 개념

// 모든 dart 프로그램은 아래와 같이 main 메서드(method)로 실행시작된다.
// 메서드는 기능을 실행하는 코드뭉치를 말한다.

void main() {
    print("Hello World");
}

// 주석(comment or annotation)은 실행되지 않는다

// 2. 데이터 타입

/*
data type 은 메모리에 저장되는 데이터 속성을 말함

다트의 데이터 타입

 Primitive Data Types
    1. String
    2. Integer
    3. Double
    4. Boolean

 Non-Primitive Data Types
    1. List
    2. Map
    3. Set

 Dynamic Data Type
    1. dynamic
    2. var

                 keyword
숫자(number) : int, double, num
문자열(String) : String
리스트(List) : List
맵(Maps) : Map (key와 value 값의 집합으로 묶음)
불리언(Boolean) : bool (참과 거짓 판단)
*/

void main() {
  /// 기본적인 data type
  String _string = "US";
  print(_string); //? US

  int _integer = 25;
  print(_integer); //? 25

  double _double = 5.8;
  print(_double); //? 5.8
  
  bool _bool = true;
  print(_bool); //? true

  /// 그 외 Data Type
  List<String> list_string = ["US", "Stars"]; // 문자열 리스트 생성
  print(list_string);
  print(list_string[0]);
  print(list_string[1]);

  List list = ["US", "Stars", 25, true, 23.3, 25]; // dynamic 데이터타입으로 리스트 생성
  print(list);

  Map<String, String> _map = {"firstName": "철수", "lastName": "박"};
  print(_map);
  print(_map["firstName"]);
  print(_map["lastName"]);

  Set<String> _set = {"Pakistan", "India", "China"}; // 문자열 set
  print(_set);

  /// Dynamic 데이터타입
  /// 다이내믹 타입은 데이터를 변경하여 입력이 가능
  dynamic _dynamic = "US";
  print(_dynamic);
  _dynamic = 25;
  print(_dynamic);

  // var 타입은 또 다른 다이내믹 데이터타입이지만 문자열 타입에 주로 사용
  var _var = "Stars";
  print(_var);

  // 숫자 입력 불가능
  //! _var = 25;

  // 숫자 입력 가능
  var age = 25;
  print(age);

  //! age = "26";
  print(age); // 26
}

/* 

변수이름 생성 규칙
  1. 변수이름은 문자,숫자,underscore(_)만을 허용
  2. 변수이름시작은 반드시 문자나 _ 이어야 함
  3. 변수이름은 숫자로 시작 불가
  4. 변수이름은 스페이스를 포함할 수 없음
  5. 변수이름은 keyword가 될 수 없음
  6. 변수이름은 reserved 용어 사용 불가  예) abstract
  7. 변수이름은 내장식별자(built-in identifier)사용 불가 예) as
  8. 변수이름은 내장타입 사용불가 예) int
  9. 변수이름은 내장함수타입 사용불가 예) print
 10. 변수이름은 내장타입상수 사용불가 예) true
*/


// 식별자 (identifier)

// 메모리에 저장된 데이터를 식별하기 위해서 정의해 놓은 이름
// 

void main() {

    // Declaring and Initializing Constant
    const con1 = 5;
    const con2 = 12;

    // Declaring and Initializing Variable
    int var1 = 5;
    int var2 = 12;

    // Changing Variable Name
    var1 = 10;
    var2 = 20;

    // Print Values
    print("First Constant : $con1");
    print("Second Constant : $con2");
    print("First Variable : $var1");
    print("Second Variable : $var2");

}

