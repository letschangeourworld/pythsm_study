
import pandas as pd                                              # 데이터프레임 생성/수정/제어용
import numpy as np                                               # 행렬,수치 계산용
import re                                                        # 문자 가공용 정규식 표현
import glob, os                                                  # 파일 리스트 불러오기용

import gensim
import gensim.downloader
from gensim.models import word2vec,Word2Vec, KeyedVectors
from gensim.models.word2vec import Word2Vec
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from konlpy.tag import Okt,Kkma,Mecab,Hannanum
okt = Okt()
kkma = Kkma()
from sklearn.ensemble import RandomForestClassifier              
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
import category_encoders as ce
import matplotlib as mpl                                         # 시각화용 : matplotlib 라이브러리 자체
import matplotlib.pyplot as plt                                  # 시각화용 : matplotlib 라이브러리내 그래프 그리기 설정용
import matplotlib.font_manager as fm                             # 시각화용 : 그래프 폰트속성 변경용
import seaborn as sns                                            # 시각화용 : seaborn 라이브러리 자체
%matplotlib inline

mpl.rcParams['axes.unicode_minus'] = False                       # 그래프내 음수 표현 폰트깨짐 방지
font_path = 'C:\\Windows\\Fonts\\HyundaiSansTextKRRegular.ttf'   # 내 컴퓨터 C드라이브내 폰트주소 불러오기
font_name = fm.FontProperties(fname=font_path).get_name()        # 폰트주소에서 폰트이름만 가져와 저장
plt.rcParams['font.family'] = font_name                          # 시각화그래프 폰트지정
plt.rcParams['font.size'] = 16                                   # 시각화그래프 폰트사이즈 지정

print('version : ', mpl.__version__)                             # matplotlib 라이브러리 현재 버전
print('설치위치 : ', mpl.__file__)                               # matplotlib 라이브러리 설치된 위치
print('설정위치 : ', mpl.get_configdir())                        # 폰트 파일을 가져오는 위치

# fn = glob.glob('./*')

df = pd.read_excel('TestRawData_20230816.xlsx')
df1 = df[df.columns[2:11]].copy()
df1 = df1.reset_index(drop=True)
df2['task'].unique()
df2 = df1[['task','work','region','property','symbol']].copy()

df2['task2'] = ''

for i in range(len(df2)):
    spt = str(df2.iloc[i,0]).split()
    rwlst = []
    for st in spt:
        w = re.sub('[^가-힣,a-zA-Z]','',st)
        rwlst.append(w)
    rwords = ' '.join(rwlst)
    df2.iloc[i,-1] = rwords

df2 = df2.dropna()

# 필요데이터 선별
X = df3[['task2','work','property']]
y = df3['symbol']

# train, test 데이터 분할 (20:80 으로 분할) 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2)

# multi-column's input data 변환
encoder = ce.OrdinalEncoder(cols = ['task2','work','property']) 
X_train = encoder.fit_transform(X_train)
X_test = encoder.transform(X_test)

# 분류모델 활성
clf = RandomForestClassifier(n_estimators = 500,
                             n_jobs = -1,
                             bootstrap = False,
                             random_state = 42,
                             criterion = 'entropy')
# 학습
clf.fit(X_train, y_train)
# 예측
y_pred = clf.predict(X_test)
# 평가
accuracy_score(y_test, y_pred)

# input성분 중요도 순위 시각화 
feature_scores = pd.Series(clf.feature_importances_, index=X_train.columns).sort_values(ascending=False)
sns.barplot(x = feature_scores, y = feature_scores.index)
plt.xlabel('Feature Importance Score')
plt.ylabel('Features')
plt.title('Visualizing Important Features')
plt.show()

# confusion matrix
print(classification_report(y_test, y_pred))








