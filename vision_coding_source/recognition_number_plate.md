## 번호판 인식 프로그램 수정

~~~python
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pytesseract                                 # 라이브러리 추가 설치
pytesseract.pytesseract.tesseract_cmd =\
'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'  # pytesseract 다운로드/설치후, 파일위치 입력

img_bgr = cv2.imread('K5_car_number_plate.png')   # 대상 이미지 불러오기
img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

fig = plt.figure(figsize=(15,6))
ax1 = fig.add_subplot(1,3,1)
plt.imshow(img_bgr)

ax2 = fig.add_subplot(1,3,2)
plt.imshow(img_rgb)

ax3 = fig.add_subplot(1,3,3)
plt.imshow(gray, cmap='gray')
plt.show()
~~~
### 이미지 형태학적 변환 (Morphological Transformation)

형태학 변환하는 이미지 프로세싱은 이미지를 분할하여 단순화, 제거, 보정을 통해 형태 파악에 목적이 있다.<BR>
이는 binary 또는 grayscale 이미지 상태에서 원본 이미지와 이미지에 가해지는 변형을 결정하는 2개의 입력값을 갖는다.<BR>
일반적으로 dilation(팽창), erosion(침식) 2개가 있고, 이를 조합하는 opening/closing이 있다.<BR>

~~~python
cv2.getStructuringElement(shape, ksize[, anchor]) # 원하는 구조로 된 커널 생성
~~~
  1. shape : 구조화 요소 커널의 모양 
      * cv2.MORPH_CROSS : 십자가형
      * cv2.MORPH_ELLIPSE : 타원형
      * cv2.MORPH_RECT : 직사각형
  2. ksize : 구조화 요소 커널의 크기
  3. anchor : 구조화 요소 커널 기준점. default값 (-1,-1)은 기준점을 중심으로 잡음.

~~~python
cv2.erode(src, kernel [,dst[,anchor[,iterations[,borderType[,borderValue]]]]]) # 침식 처리
~~~

&nbsp;&nbsp;&nbsp;  생성한 커널에 0이 하나라도 있으면 픽셀을 제거하는 방법 → 검은색 영역(0)이 흰색영역(1)을 침식해 들어감<BR>
&nbsp;&nbsp;&nbsp;  이미지 내 작은 물체(object)가 있으면 제거할 수 있음<BR>
  1. src : 입력이미지 (채널수 상관없음, 사용이미지종류 → CV_8U,CV_16U,CV_16S,CV_32F,CV_64F)
  2. kernel : 구조화 요소커널 → cv2.getStructuringElement로 생성
  3. anchor : 기준점
  4. iterations : 침식 반복 횟수

~~~python
cv2.dilate(src, kernel [,dst[,anchor[,iterations[,borderType[,borderValue]]]]]) # 팽창 처리
~~~
&nbsp;&nbsp;&nbsp;  생성한 커널에 1이 하나라도 있으면 픽셀을 제거하는 방법 → 흰색 영역(1)이 더 넓어짐<BR>
&nbsp;&nbsp;&nbsp;  경계가 조금 부드러워지고 구멍이 메꿔지는 효과가 있음<BR>
  
~~~python
cv2.morphologyEx(src, op, kernel [,dst[,anchor[,iterations[,borderType[,borderValue]]]]]) # Opening & Closing
~~~
&nbsp;&nbsp;&nbsp;  Opening : 침식적용후 팽창적용, 영역이 점점 둥글어 짐, 점잡음,작은물체,돌기 제거용<BR>
&nbsp;&nbsp;&nbsp;  Closing : 팽창적용후 침식적용, 영역과 영역이 서로 붙음, 이미지 전체 윤곽 파악용<BR>
  1. src : 입력이미지
  2. op : 형태학적 연산
     * cv2.MORPH_OPEN     : 침식후 팽창
     * cv2.MORPH_CLOSE    : 팽창후 침식
     * cv2.MORPH_GRADIENT : 팽창에서 침식을 빼 줌
     * cv2.MORPH_TOPHAT   : src에서 OPENING을 빼 줌
     * cv2.MORPH_BLACKHAT : CLOSING에서 src를 빼 줌
  3. kernel : 구조화된 커널
  4. anchor : 기준점
  5. iterations : 반복 횟수

~~~python
cv2.add(src1, src2 [,dst[,dtype]]])  # 두 개의 이미지 합성
~~~
&nbsp;&nbsp;&nbsp; 두 개 이미지 덧셈 결과가 255보다 크면 픽셀값을 255로 설정
  1. src1  : 첫 번째 이미지/영상
  2. src2  : 두 번째 이미지/영상
  3. dst   : 덧셈 연산 결과 이미지/영상
  4. mask  : 영역 지정
  5. dtype : 출력 결과(dst) 타입 (cv2.CV_8U, cv2.CV_32F 등)

~~~python
cv2.substract(src1, src2, dst=None, mask=None, dtype=None)   # 두 개의 이미지 뺄셈 연산, 파라미터는 덧셈과 같음
~~~
&nbsp;&nbsp;&nbsp; 영상간 뺄셈 결과가 0보다 작으면 픽셀값을 0으로 설정

~~~python
structuringElement = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))        # 원하는 형태 구조로 된 커널 생성
imgTopHat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, structuringElement)      # 원본 이미지에서 잡티를 제거해 줌
imgBlackHat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, structuringElement)  # 이미지 전체 윤곽을 얻고 거기에서 원본 이미지를 제거
imgGrayscalePlusTopHat = cv2.add(gray, imgTopHat)                             # 두 개의 이미지 합성 (원본이미지와 잡티제거이미지 합성)
gray1 = cv2.subtract(imgGrayscalePlusTopHat, imgBlackHat)                     # 윤곽선 외의 이미지는 0(검정색)으로 변경

# 원본이미지에서 잡티제거처리
fig = plt.figure(figsize = (15,12))
ax1 = fig.add_subplot(2,2,1)
plt.title('TopHat')
plt.imshow(imgTopHat, cmap='gray')

# 이미지 윤곽만 표현
ax2 = fig.add_subplot(2,2,2)
plt.title('BlackHat')
plt.imshow(imgBlackHat, cmap='gray')

# 잡티제거후 흑백처리
ax3 = fig.add_subplot(2,2,3)
plt.title('GrayScale + TopHat')
plt.imshow(imgGrayscalePlusTopHat, cmap='gray')

# 윤곽선외 검정색처리
ax4 = fig.add_subplot(2,2,4)
plt.title('GrayScale + TopHat - BlackHat')
plt.imshow(gray1, cmap='gray')
plt.show()
~~~

~~~python
cv2.GaussianBlur(src, ksize, sigmaX[, dst[, sigmaY[, borderType=BORDER_DEFAULT]]] )
~~~
&nbsp;&nbsp;&nbsp; 이미지내 필터링 대상물체에 가까이 있는 픽셀과 멀리있는 픽셀 모두 같은 가중치를 두어 평균을 계산해 왔었다.<br>
&nbsp;&nbsp;&nbsp; 그런데 픽셀에 동일한 평균 가중치를 두는 것에서 표준정규확률분포공식(가우시안)에 근거하여 픽셀에 가중치를 주어<br>
&nbsp;&nbsp;&nbsp; 이미지 처리하는 것을 가우시안 필터링이라고 한다.<br>

![image1](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2F3hxC7%2FbtqJU4lkGql%2FDctAZcntV6dKoG0JaSgZYK%2Fimg.png)<br>
![image2](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FcUECiH%2FbtqJUME9AwC%2FSWsLYpI5bmnUSgBNb5Fq1K%2Fimg.png)

  1. src : 입력 이미지/영상
  2. ksize : 가우시안 커널 크기. (0,0)을 지정하면 sigma값에 의해 자동 결정됨
  3. sigmaX : x방향 sigma
  4. sigmaY : y방향 sigma, 0이면 sigmaX와 같게 설정됨
  5. borderType : 가장자리 픽셀확장 방식

~~~python
# 가우시안 이미지처리 sigma값에 따른 사진모습 테스트
fig = plt.figure(figsize = (15,12))
for sigma in range(1,5):
  dst = cv2.GaussianBlur(gray1, ksize=(5,5), sigma)
  desc = 'sigma = {}'.format(sigma)
  cv2.putText(dst, desc, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,255,255), 1, cv2.LINE_AA)
  ax = fig.add_subplot(2,2,sigma)
  plt.imshow(dst, cmap='gray')
plt.show()
~~~
~~~python
cv2.threshold(src, thresh, maxval, type)
~~~
  1. src : 그레이스케일 이미지
  2. thresh : 기준값
  3. maxValue : 기준값을 넘었을 때 적용할 값
  3. thresholdType  : 임계처리 유형
      - THRESH_BINARY     : 기준값을 넘으면 최대값, 아니면 0
      - THRESH_BINARY_INV : 기준값을 넘으면 0, 아니면 최대값
      - THRESH_TRUNC      : 기준값을 넘으면 기준값, 아니면 최대값
      - THRESH_TOZERO     : 기준값을 넘으면 원래값, 아니면 0
      - THRESH_TOZERO_INV : 기준값을 넘으면 0, 아니면 원래값

~~~python
# 적응임계처리
cv2.adaptiveThreshold(src, maxValue, adaptiveMethod, thresholdType, blockSize, C)
~~~
  1. src : 그레이스케일 이미지
  2. maxValue : 기준값을 넘었을 때 적용할 값
  3. adaptiveMethod : 영역 내에서 기준값을 계산하는 방법
      - ADAPTIVE_THRESH_MEAN_C     : 영역 내의 평균값에 c를 뺀 값을 기준값으로 사용 (평균적응 임계처리)
      - ADPATIVE_THRESH_GAUSSIAN_C : 영역에 추후 설명할 가우시안 블러를 적용한 후, C를 뺀 값을 기준값으로 사용 (가우시안블러 적응임계처리)
  4. thresholdType  : 임계처리 유형
      - THRESH_BINARY     : 기준값을 넘으면 최대값, 아니면 0
      - THRESH_BINARY_INV : 기준값을 넘으면 0, 아니면 최대값
      - THRESH_TRUNC      : 기준값을 넘으면 기준값, 아니면 최대값
      - THRESH_TOZERO     : 기준값을 넘으면 원래값, 아니면 0
      - THRESH_TOZERO_INV : 기준값을 넘으면 0, 아니면 원래값

~~~python
maxval, thresh = 255, 127
ret, th1 = cv2.threshold(gray1,
                         thresh,
                         maxval,
                         cv2.THRESH_BINARY_INV)
blockSize, C = 15, 25
th2 = cv2.adaptiveThreshold(gray1,
                            maxval,
                            cv2.ADAPTIVE_THRESH_MEAN_C,
                            cv2.THRESH_BINARY_INV,
                            blockSize,
                            C)
th3 = cv2.adaptiveThreshold(gray1,
                            maxval,
                            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                            cv2.THRESH_BINARY_INV,
                            blockSize,
                            C)
images = [gray1,th1,th2,th3]
titles = ['Original','Threshold (Binary_INV)',
          'Adaptive_Thresh_Mean (Binary_INV)',
          'Adaptive_Thresh_Gaussian (Binary_INV)']

fig = plt.figure(figsize = (12,8))
for i in range(4):
    plt.subplot(2,2,i+1)
    plt.imshow(images[i], 'gray')
    plt.title(titles[i])
    plt.axis('off')
plt.tight_layout()
plt.show()
~~~

~~~python
#윤곽선
contours, _ = cv2.findContours(img_thresh, 
                               mode=cv2.RETR_LIST, 
                               method=cv2.CHAIN_APPROX_SIMPLE)

temp_result = np.zeros((height, width, channel), dtype=np.uint8)
cv2.drawContours(temp_result, contours=contours, contourIdx=-1, color=(255, 255, 255))

# 컨투어의 사각형 범위 찾기
temp_result = np.zeros((height, width, channel), dtype = np.uint8)

contours_dict = []
for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)
    cv2.rectangle(temp_result,
                  pt1 = (x, y),
                  pt2 = (x+w, y+h),
                  color = (255, 255, 255),
                  thickness = 2)
    
    # insert to dict
    contours_dict.append({'contour': contour,
                          'x': x,
                          'y': y,
                          'w': w,
                          'h': h,
                          'cx': x + (w / 2),
                          'cy': y + (h / 2) })

contours_dict

# 어떤게 번호판처럼 생겼는지?
MIN_AREA = 80
MIN_WIDTH, MIN_HEIGHT = 2, 8
MIN_RATIO, MAX_RATIO  = 0.25, 1.0

possible_contours = []
cnt = 0
for d in contours_dict:
    area = d['w'] * d['h']
    ratio = d['w'] / d['h']
    
    if area > MIN_AREA and \
       d['w'] > MIN_WIDTH and \
       d['h'] > MIN_HEIGHT and \
       MIN_RATIO < ratio < MAX_RATIO:
        d['idx'] = cnt
        cnt += 1
        possible_contours.append(d)

possible_contours

# visualize possible contours
temp_result = np.zeros((height, width, channel), dtype=np.uint8)

for d in possible_contours:
    cv2.drawContours(temp_result, d['contour'], -1, (255, 255, 255))
    cv2.rectangle(temp_result,
                  pt1 = (d['x'], d['y']), 
                  pt2 = (d['x']+ d['w'], d['y'] + d['h']),
                  color = (255, 255, 255),
                  thickness = 2)

# 리얼 번호판 추려내기
MAX_DIAG_MULTIPLYER = 5   # 5
MAX_ANGLE_DIFF = 12.0     # 12.0
MAX_AREA_DIFF = 0.5       # 0.5
MAX_WIDTH_DIFF = 0.8
MAX_HEIGHT_DIFF = 0.2
MIN_N_MATCHED = 3         # 3

def find_chars(contour_list):
    matched_result_idx = []
    for d1 in contour_list:
        matched_contours_idx = []
        for d2 in contour_list:
            if d1['idx'] == d2['idx']:
                continue
            
            dx = abs(d1['cx'] - d2['cx'])
            dy = abs(d1['cy'] - d2['cy'])
            diagonal_length1 = np.sqrt(d1['w'] ** 2 + d1['h'] ** 2)
            distance = np.linalg.norm(np.array([d1['cx'], d1['cy']]) - np.array([d2['cx'], d2['cy']]))
            
            if dx == 0:
                angle_diff = 90
            else:
                angle_diff = np.degrees(np.arctan(dy / dx))
            
            area_diff = abs(d1['w'] * d1['h'] - d2['w'] * d2['h']) / (d1['w'] * d1['h'])
            width_diff = abs(d1['w'] - d2['w']) / d1['w']
            height_diff = abs(d1['h'] - d2['h']) / d1['h']
            
            if distance < diagonal_length1 * MAX_DIAG_MULTIPLYER and \
               angle_diff < MAX_ANGLE_DIFF and \
               area_diff < MAX_AREA_DIFF and \
               width_diff < MAX_WIDTH_DIFF and \
               height_diff < MAX_HEIGHT_DIFF:
                matched_contours_idx.append(d2['idx'])
        
        # append this contour
        matched_contours_idx.append(d1['idx'])
        
        if len(matched_contours_idx) < MIN_N_MATCHED:
            continue
        
        matched_result_idx.append(matched_contours_idx)
        
        unmatched_contour_idx = []
        for d4 in contour_list:
            if d4['idx'] not in matched_contours_idx:
                unmatched_contour_idx.append(d4['idx'])
        
        unmatched_contour = np.take(possible_contours, unmatched_contour_idx)
        
        # recursive
        recursive_contour_list = find_chars(unmatched_contour)
        
        for idx in recursive_contour_list:
            matched_result_idx.append(idx)
        
        break
    
    return matched_result_idx

result_idx = find_chars(possible_contours)

matched_result = []
for idx_list in result_idx:
    matched_result.append(np.take(possible_contours, idx_list))

# visualize possible contours
temp_result = np.zeros((height, width, channel), dtype=np.uint8)

for r in matched_result:
    for d in r:
        cv2.drawContours(temp_result, d['contour'], -1, (255, 255, 255))
        cv2.rectangle(temp_result,
                      pt1 = (d['x'], d['y']),
                      pt2 = (d['x']+d['w'], d['y']+d['h']),
                      color = (255, 255, 255),
                      thickness = 2)

# 똑바로 돌리기
PLATE_WIDTH_PADDING = 1.3   # 1.3
PLATE_HEIGHT_PADDING = 1.5  # 1.5
MIN_PLATE_RATIO = 3
MAX_PLATE_RATIO = 10

plate_imgs = []
plate_infos = []

for i, matched_chars in enumerate(matched_result):
    sorted_chars = sorted(matched_chars, key=lambda x: x['cx'])
    
    plate_cx = (sorted_chars[0]['cx'] + sorted_chars[-1]['cx']) / 2
    plate_cy = (sorted_chars[0]['cy'] + sorted_chars[-1]['cy']) / 2
    
    plate_width = (sorted_chars[-1]['x'] + sorted_chars[-1]['w'] - sorted_chars[0]['x']) * PLATE_WIDTH_PADDING
    
    sum_height = 0
    for d in sorted_chars:
        sum_height += d['h']
    
    plate_height = int(sum_height / len(sorted_chars) * PLATE_HEIGHT_PADDING)
    triangle_height = sorted_chars[-1]['cy'] - sorted_chars[0]['cy']
    triangle_hypotenus = np.linalg.norm(np.array([sorted_chars[0]['cx'], sorted_chars[0]['cy']]) 
                                        - np.array([sorted_chars[-1]['cx'], sorted_chars[-1]['cy']]))
    angle = np.degrees(np.arcsin(triangle_height / triangle_hypotenus))
    rotation_matrix = cv2.getRotationMatrix2D(center = (plate_cx, plate_cy), angle = angle, scale = 1.0)
    img_rotated = cv2.warpAffine(img_thresh, M = rotation_matrix, dsize = (width, height))
    img_cropped = cv2.getRectSubPix(img_rotated,
                                    patchSize=(int(plate_width), int(plate_height)),
                                    center=(int(plate_cx), int(plate_cy)))
    
    if img_cropped.shape[1] / img_cropped.shape[0] < MIN_PLATE_RATIO or \
       img_cropped.shape[1] / img_cropped.shape[0] < MIN_PLATE_RATIO > MAX_PLATE_RATIO:
        continue
    
    plate_imgs.append(img_cropped)
    plate_infos.append({'x': int(plate_cx - plate_width / 2),
                        'y': int(plate_cy - plate_height / 2),
                        'w': int(plate_width),
                        'h': int(plate_height)})

# 최종 확인
longest_idx, longest_text = -1, 0

plate_chars = []
for i, plate_img in enumerate(plate_imgs):
    plate_img = cv2.resize(plate_img,
                           dsize = (0, 0),
                           fx = 1.6,
                           fy = 1.6)
    _, plate_img = cv2.threshold(plate_img,
                                 thresh = 0.0,
                                 maxval = 255.0,
                                 type = cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    
    # find contours again (same as above)
    contours, _ = cv2.findContours(plate_img,
                                   mode = cv2.RETR_LIST,
                                   method = cv2.CHAIN_APPROX_SIMPLE)
    
    plate_min_x, plate_min_y = plate_img.shape[1], plate_img.shape[0]
    plate_max_x, plate_max_y = 0, 0
    
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        ratio = w / h
        
        if area > MIN_AREA and \
           w > MIN_WIDTH and \
           h > MIN_HEIGHT and \
           MIN_RATIO < ratio < MAX_RATIO:
            if x < plate_min_x:
                plate_min_x = x
            if y < plate_min_y:
                plate_min_y = y
            if x + w > plate_max_x:
                plate_max_x = x + w
            if y + h > plate_max_y:
                plate_max_y = y + h
    
    img_result = plate_img[plate_min_y:plate_max_y, plate_min_x:plate_max_x]
    img_result = cv2.GaussianBlur(img_result, ksize = (3, 3), sigmaX = 0)
    _, img_result = cv2.threshold(img_result, thresh = 0.0, maxval = 255.0, type = cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    img_result = cv2.copyMakeBorder(img_result, top = 10, bottom = 10, left = 10, right = 10, borderType = cv2.BORDER_CONSTANT, value=(0,0,0))
    chars = pytesseract.image_to_string(img_result, lang='kor', config='')
    
    result_chars = ''
    has_digit = False
    for c in chars:
        if ord('가') <= ord(c) <= ord('힣') or c.isdigit():
            if c.isdigit():
                has_digit = True
            result_chars += c
    
    print(result_chars)
    plate_chars.append(result_chars)
    
    if has_digit and len(result_chars) > longest_text:
        longest_idx = i
    
    plt.subplot(len(plate_imgs), 1, i+1)
    plt.imshow(img_result, cmap='gray')
    plt.show()

~~~
