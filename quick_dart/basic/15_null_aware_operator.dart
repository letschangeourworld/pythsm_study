// null일 경우 특정값 입력

void main() {
  var name = null;
  name ??= 'Pythsm';
  print(name);

  name ??= 'Dev';
  print(name);
}
