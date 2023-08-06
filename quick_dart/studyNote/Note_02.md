
### □ Conditional Statement, 조건문

- if/if~else

      [1]
      if (condition) {
        execute statement;
      }

      [2]
      if (condition) {
        execute statement1;
      } else {
        execute statement2;
      }

      [ex]
      if (a == 1) {
        print('The value of a is 1');
      } else {
        print('The value of a is not 1');
      }

- switch 

      [1]
      switch(variable) {
      case value1:
        execute statement1;
        break;
      case value2:
        execute statement2;
        break;
      default:
        execute statement3;
      }

      [ex]
      var number = 1;
      switch(number) {
      case 1:
        print('number is 1');
        break;
      case 2:
        print('number is 2');
        break;
      default:
        print('number is the rest of them');
      }

- assert
      - condition 이 false 이면 error 발생
      - debug mode 에서만 동작하고 프로그램 실행의 release mode 에서 미동작

      [1]
      assert(condition);

      [ex]
      assert(a > 0);


### □ Iteration or Loop Statement, 반복문

- for

      [1]
      for (initialization; condition; operator) {
            execute statement;
      }

      [ex]
      for (int i = 1; i < 5; i++) {
            print('i = $i');
      }

- while
- do~while








