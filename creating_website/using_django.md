- 가상환경 생성 : python -m venv (venvname)  -> conda에서 가상환경 생성해도 됨
- 가상환경 실행 : source (venvname)/Scripts/activate -> conda에서 가상환경 실행해도 됨
- 가상환경 종료 : deactivate -> conda에서 가상환경 종료
- 장고설치      : pip install django
- 장고삭제      : pip uninstall django
- 특정버전 설치 : pip install django==버전(ex:3.0.1)
- 서버실행      : python manage.py runserver
- 서버종료      : ctrl + c
- 프로젝트 생성 : django-admin startproject (project name)

<생성된 디렉토리>
~~~python
firstweb
├─manage.py
└─firstweb
   settings.py
   urls.py
   wsgi.py
   __init__.py
~~~
- manage.py   : 사이트 관리를 도와주는 역할
- settings.py : 웹사이트 설정
- urls.py     : urlresolver(우편배달부)가 사용하는 패턴목록을 포함

1. settings.py 수정
~~~python
  TIME_ZONE = 'Asia/Seoul'
  STATIC_URL = '/static/'
  STATIC_ROOT = os.path.join(BASE_DIR, 'static')
  ALLOWED_HOSTS = ['127.0.0.1', '.pythonanywhere.com']
~~~
2. DB 설정
  - 콘솔창에서 python manage.py migrate 실행
  - 확인 : python manage.py runserver

3. 장고 모델 생성 -> 모델을 생성하면 DB에 저장할 수가 있다.
~~~
(myweb) python manage.py startapp blog
~~~
~~~
firstweb
    ├── firstweb
    |       __init__.py
    |       settings.py
    |       urls.py
    |       wsgi.py
    ├── manage.py
    └── blog
        ├── migrations
        |       __init__.py
        ├── __init__.py
        ├── admin.py
        ├── models.py
        ├── tests.py
        └── views.py
~~~
<settings.py>
~~~
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blog',
]
~~~
<models.py>
~~~python
from django.conf import settings
from django.db import models
from django.utils import timezone

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(
            default=timezone.now)
    published_date = models.DateTimeField(
            blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title
~~~
~~~
(myweb) python manage.py makemigrations blog
(myweb) python manage.py migrate blog
~~~



