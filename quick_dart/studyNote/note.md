
## Installation & Configuration

1. Flutter Installation ▷ C drive <br>
   Dart-sdk download and installation if needed <br>
2. Configuration Check with flutter doctor <br>
    - java latest update, VS development upgrade etc. <br>
3. Android Studio Installation and configuration <br>
    - settings ▷ Plugins ▷ flutter installation and dart <br>
        - path selection : flutter install files directory <br>
        - path selection : dart-sdk install files directory <br>
    -  File ▷ New Project ▷ flutter or dart <br>
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

## Dart Language

* class ▷ compile (storing to memory) ▷ instance (finished storing to memory)
  
* variable type keyword : <b>var, dynamic, int, String, double, bool,</b> etc.
* There is No <b>public, protected, private </b>keyword
* private identifiers : use <b>underscore( _ )</b> in front of variables.
* debug mode and release mode

* built-in identifiers (내장식별자, 내장함수) <br>
  - <b>abstract, as, dynamic, export, factory, Function,
  - get, import, implements, static, typedef, mixin, set, etc.</b>
* Contextual keyword (문맥적 키워드)
  - <b>sync, async, hide, on, show</b> <br>
* 2 keywords can't be used as an identifier in 'async','async*','sync*' methods <br>
  - <b>await, yield</b> <br>
* Reserved words <br>
  - <b>assert, break, case, catch, class, const, continue, do, else,
  - enum, extends, false, final, finally, for, if, in, is, new,
  - null, return, super, switch, this, throw, true, try, var,
  - void, while, with, etc </B>
<br>
<br>

<b>Comment, 주석</b> <br>
//, /* contents */ <br>

<br>
<br>

<b>Data Type </b> <br>
   - num     : int or double ▷ supertype(상위타입)
   - int     : 정수
   - double  : 실수
   - String  : 문자열
   - bool    : true or false
   - var     : 타입미지정 : 타입추정하여 자동지정 ▷ 타입변경불가
   - dynamic : 타입미지정 ▷ 타입변경가능
   - List    : 리스트
   - Set     : 데이터셋 ▷ 순서 X, 중복 X
   - Map     : key, value 값 형태 데이터셋

<br>
<br>

<b>Constant, 상수</b> <br>
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
      - 프로그램 실행시 변수값이 알 수 없는 이유로 변경되는 것을 사전에 방지하기 위해 상수사용 필수임<br>














    