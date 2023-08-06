
### Class

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
      var student = Human(); // var는 변수타입 자동생성, student타입은 Human 타입
      var teacher = Human(); // var는 변수타입 자동생성, teacher타입은 Human 타입
      Human mankind = Human(); // mankind는 변수타입을 Human으로 지정해줌

      student.name = 'Emily';
      teacher.name = 'Tomas';
      mankind.name = 'man';

      print('student name : ${student.getName()}');
      print('teacher name : ${teacher.getName()}');
      print('mankind name : ${mankind.getName()}');
    }


     __Class (자동차 생산공장)_____
    | class name (생산차 제조명)   |
    | member variables (생산재료)  |
    | member methods (생산공법)    |
    | Constructor (주문서,생산착수) | 



### Constructor, 생성자
- instance 생성시 호출되는 '인스턴스 초기화 method'임


#### 1. Default Constructor

#### 2. Named Constructor

#### 3. Initializer List

#### 4. Redirecting Constructor

#### 5. Constant Constructor

#### 6. Factory Constructor



    
