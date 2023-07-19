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

data type : 숫자(number),문자열(String), 리스트(List), 맵(Maps),불리언(Boolean)

숫자(number) : int, double, num
문자열(String) : String
리스트(List) : List
맵(Maps) : Map (key와 value 값의 집합으로 묶음)
불리언(Boolean) : bool (참과 거짓 판단)
*/


// 3. 식별자 (identifier)

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



