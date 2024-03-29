
## ◈ Installation & Configuration

### 1.1. Flutter Installation ▷ C drive
   - Dart-sdk download and installation if needed
### 1.2. Configuration Check with flutter doctor <br>
   - java latest update, VS development upgrade etc. <br>
### 1.3. Android Studio Installation and configuration <br>
   - settings ▷ Plugins ▷ flutter installation and dart <br>
       - path selection : flutter install files directory <br>
       - path selection : dart-sdk install files directory <br>
   - File ▷ New Project ▷ flutter or dart <br>
   - Android SDK Manager <br>
   - SDK Tools <br>
       - Android SDK Build-Tools 34 <br> 
       - CMake <br>
       - Android SDK Comman-line Tools <br>
       - SDK Platforms : Android 11 installation <br>
   - Device Manager <br>
       - Create Device <br>
       - Phone pixel 2 api 30 : Android 11 <br>
<br>

## ◈ Dart Language

#### 1. class ▷ compile (storing to memory) ▷ instance (finished storing to memory)
#### 2. variable type keyword : <b>var, dynamic, int, String, double, bool,</b> etc.
#### 3. There is No <b>public, protected, private </b>keyword
#### 4. private identifiers : use <b>underscore( _ )</b> in front of variables.

#### 5. built-in identifiers (내장식별자, 내장함수) <br>
       abstract, as, dynamic, export, factory, Function,
       get, import, implements, static, typedef, mixin, set, etc.
#### 6. Contextual keyword (문맥적 키워드)
       sync, async, hide, on, show
#### 7. 2 keywords can't be used as an identifier in 'async','async*','sync*' methods
       await, yield
#### 8. Reserved words
       assert, break, case, catch, class, const, continue, do, else,
       enum, extends, false, final, finally, for, if, in, is, new,
       null, return, super, switch, this, throw, true, try, var,
       void, while, with, etc </B>
<br>
<br>
<b>Comment, 주석</b> <br>
//, /* contents */ <br>
<br>
<br>

### ◇ Data Type
    num     : int or double ▷ supertype(상위타입)
    int     : 정수
    double  : 실수
    String  : 문자열
    bool    : true or false
    var     : 타입미지정(undefined type) : 타입추정하여 자동지정 ▷ 타입변경불가
    dynamic : 타입미지정(undefined type) ▷ 타입변경가능
    List    : 리스트
    Set     : 데이터셋 ▷ 순서 X & 중복 X
    Map     : key, value 값 형태 데이터셋
<br>
<br>

### Constant, 상수
   - final : 값변경 불가능, variable 맨 앞에 붙임, runtime시 상수화
   - const : 값변경 불가능, variable 맨 앞에 붙임, compiletime시 상수화
   - compiletime과 runtime 시점 상수화란? <br>
      - compile은 소스코드를 기계어로 변경해 주는 작업으로 문법상 이상이 없으면 error가 없음.<br>
      - 그러나 compile시 변수에 값이 없는 상태, null 이 발견되면 compile error 발생함.<br>
      - 값이 미지정된 변수를 초기화하여 지정하라는 error message임.<br>
      - 이 때, const 대신 final을 사용하면 어떻게 될까?<br>
      - 이미 compile된 전체 프로그램을 실제로 실행시키는 Run을 하는데 이 시점이 runtime임.<br>
      - compile시에는 변수값을 받을 수 없다는 것을 컴퓨터가 final로 알고 있기 때문에,<br>
      - 전체프로그램이 실행되면서 생성된 변수값을 넘겨 받게 되어 error가 없게 됨. <br>
      - 그러나 const에서 null safety 확보, syntax error수정 등을 진행하는 것이 좋고,<br>
      - 그런 것이 아니라면 final도 관계없음.<br>
      - 프로그램 실행시 변수값이 알 수 없는 이유로 변경되는 것을 사전에 방지하기 위해 상수사용 필수.
<br>
<br>

### ◇ Function, 함수

#### 1. 다트언어는 모든 것이 객체(object)임.
#### 2. Variable이 Function참조 및 전달가능

<pre>
   <code>
      // multi function 안에 add and sub function이 참조됨
      int add(int a, int b) {
         return a + b;
      }
      int sub(int a, int b) {
         return a - b;
      }
      int multi(int a, int b) {
         return a + b;
      }
      main() {
         int a = 10;
         int b = 5;
         print('${a + b} + ${a - b} = ${multi(add(a,b), sub(a, b))}');
      }

      // 15 * 5 = 75
   </code>
</pre>
<br>

#### 3. Optional parameter (선택매개변수)
- 매개변수에 중괄호({})를 붙여서 표현하면 나중에 값을 입력해도 되고 안 해도 됨
- 매개변수에 대괄호([])를 붙이면 초기값을 지정할 수 있고, 나중에 초기값과 다른 값을 입력하면, 초기값은 무시되고 현재 입력한 값을 사용함

#### 3.1 Named optional parameter (이름지정된 선택매개변수)
 
      int getYear(String Sorento, {String Genesis, String EV6}) {}      
      int getYear('Sorento', {Genesis : 2019, EV6 : 2023}) {}

#### 3.2 Positional optional parameter (위치적 선택매개변수)

      String getName(String carName, [String carHost = 'Emily', String numberPlate = '62구 9999']) {
         return '$carName : , $carHost : , $numberPlate : ';
      }
      
      main() {
         print('${getName('Sorento')}');
         print('${getName('Sorento', 'Peter')}');
      }

#### 3.3 anonymous function (익명함수) & lambda expression
- 매개변수값을 나중에 입력하고 임의의 변수명으로 표현
- 람다표현은 arrrow function 으로 { return } 부분을 대체하여 한 줄로 표현가능

<pre>
   <code>
int add(int a, int b) {
   return a + b;
}

var multi = (_a, _b) {
   return _a * _b;
};

sub(_a, _b) => _a - _b; // 람다표현식

main() {
   int a = 10;
   int b = 5 ;
  
   print('$a + $b = ${add(a, b)}');
   print('$a * $b = ${multi(a,b)}');
   print('$a - $b = ${sub(a,b)}' );
}
   </code>
</pre>
<br>

### ◇ Operator, 연산자

#### 1. Type Inspection Operator
    as  : supertype conversion (상위타입으로 변환)
    is  : ~ 이면 true
    is! : ~ 이면 false

<pre>
   <code>
class Mammal {
  String name = 'Mammal';
}
class Seal extends Mammal {
  @override
  String name = 'Seal';
}
class Whale extends Mammal {
  @override
  String name = 'Whale';
}
void main() {
  Seal seal = Seal();
  Whale whale = Whale();

  Mammal mammal1 = seal;
  Mammal mammal2 = whale;

  print('mammal1.name = ${mammal1.name}');
  print('mammal2.name = ${mammal2.name}');

  if (seal is Whale) {
    print('Seal is Whale');
  } else {
    print('Seal is not Whale');
  }
}
   </code>
</pre>

    mammal1.name = Seal
    mammal2.name = Whale
    Seal is not Whale


### ◇ Condition Expression, 조건표현

#### 1. 조건 ? 표현식1 : 표현식2;
- 조건이 참이면 표현식1, 거짓이면 표현식2

#### 2. 좌항?.우항
- 좌항이 null값이면 null을 리턴, 그렇지 않으면 우항 리턴
- ex) mammal?.name mammal이 → null값이면 null 리턴, 아니면 mammal.name 리턴

#### 3. 좌항??우항
- 좌항이 null이 아니면 좌항 리턴, 아니면 우항 리턴
- ex) mammal.name ?? 'mammal name' → mammal.name이 null이면 'mammal name' 리턴

### ◇ Cascade Expression
- 클래스 안에 있는 멤버함수를 반복적으로 불러올 때, 이를 생략하는 방법
- ex) Mammal mammal = Mammal()
      ..name = 'seal'
      ..habitatCode(12)
      ..speciesInfo(); 
- .. 으로 원래 적어줘야 할 mammal.name 에서 mammal을 생략할 수 있게 됨











    
