
### ◈ Class

    [1]
    class 클래스명 {
      멤버변수
      멤버함수
    }

    [ex1]
    class Person {   // 클래스명 첫글자는 대문자
      String name;   // 멤버변수
      getName() {    // 멤버함수, 첫글자는 소문자
        return name;
      }
    }

    [ex2]
    class Human {
      String name; // String은 타입을 지정하는 class 이므로 첫글자가 대문자임
      int age;

      getName() {
        return name;
      }
    }
    main() {
      var student = Human();   // var는 변수타입 자동생성, student타입은 Human 타입
      var teacher = Human();   // var는 변수타입 자동생성, teacher타입은 Human 타입
      Human mankind = Human(); // mankind는 변수타입을 Human으로 지정해줌

      student.name = 'Emily';
      teacher.name = 'Tomas';
      mankind.name = 'man';

      print('student name : ${student.getName()}');
      print('teacher name : ${teacher.getName()}');
      print('mankind name : ${mankind.getName()}');
    }

<br>

     __  Class (자동차 생산공장) ____
    |                               | 
    | class name (생산차 제조명)     |
    |  member variables (생산정보)   |
    |  member methods (생산공법)     |
    |  Constructor (주문서,생산착수)  |
    |______________________________ |
    
    ※ 주문이 들어오면 각각의 다양한 생산정보대로 다양한 차를 생산한다. 
       → 한 공장에서 여러가지 옵션으로 생산된 차 (세부적인 표현) : instance (인스턴스)
       → 한 공장에서 만들어진 차 (일반적인 표현) : object (객체)
       → 한 공장에서 차가 만들어지는 과정 : 인스턴스화
       

### ◈ Constructor, 생성자
- instance 생성시 호출되는 '인스턴스 초기화 method'임.
- 자동차 생산공장이 고객 주문이 들어와야 공장이 움직이듯이 constructor가 있어야 생산이 시작됨.

#### 1. Default Constructor

#### 2. Named Constructor

#### 3. Initializer List

#### 4. Redirecting Constructor

#### 5. Constant Constructor

#### 6. Factory Constructor

<br>
<br>
<br>
<br>
<br>

<pre>
    <code>
class Foo {
  String item;
  int cnt;
  Foo(this.item, this.cnt);
}

class Foo2 extends Foo {
  double ratio;
  Foo2(super.item,super.cnt,this.ratio);
}

void main() {
  Foo2 yourFoo = Foo2('table', 5, 2.5);
  var Foo2(:item,:cnt,:ratio) = yourFoo;
  print(' 품명: $item\n 판매량: $cnt\n 판매율: $ratio %');
}
    </code>
</pre>

        품명: table
        판매량: 5
        판매율: 2.5 %

