
# jupyter notebook에서 복북해서 실행해도 됨
# Mailing Packages Installation

import pandas as pd                              # 엑셀 불러오기
import email,smtplib,ssl,os,copy                 # smtplib: 메일 전송을 위한 패키지
from email import encoders                       # 파일전송을 할 때 이미지나 문서 동영상 등의 파일을 문자열로 변환할 때 사용할 패키지
from email.mime.base import MIMEBase             # 파일을 전송할 때 사용되는 모듈
from email.mime.multipart import MIMEMultipart   # 메시지를 보낼 때 메시지에 대한 모듈
from email.mime.text import MIMEText             # 본문내용을 전송할 때 사용되는 모듈
from email.header import Header
from email.utils import formataddr
from smtplib import SMTP_SSL,SMTP
from email.mime.application import MIMEApplication
from string import Template                      # 문자열 템플릿 모듈
from email.mime.image import MIMEImage

# 메일을 보내는 클래스 선언
class EmailHTMLImageContent:
  def __init__(self, subject, attach_file_name, template, template_params):
      
      assert isinstance(template, Template)
      assert isinstance(template_params, dict)
      self.msg = MIMEMultipart()
      
      # 제목설정
      self.msg['Subject'] = subject
      
      # 본문설정
      message = template.safe_substitute(**template_params)     # ${변수}의 변수를 원하는 문자로 일괄치환
      mime_msg = MIMEText(message,'html')                       # MIME HTML 문자열 생성
      self.msg.attach(mime_msg)
      
      # 첨부파일 추가
      with open(attach_file_name, "rb") as f:
          af = MIMEApplication(f.read())
          af.add_header('Content-Disposition','attachment',filename=attach_file_name)
      
      self.msg.attach(af)
      
  def get_message(self, sender_addr, receiver_addr):
      mm = copy.deepcopy(self.msg)
      mm['From'] = sender_addr             # 발신자
      mm['To']   = receiver_addr           # 수신자 리스트
      return mm

class EmailSender:
  # 네이버 메일 기준 smtp서버명과 포트 사용함 -> 다른 메일서버를 사용하려면 변경해야 함
  def __init__(self, mail_server='smtp.naver.com', mail_port = 465):
      self.host = mail_server
      self.port = mail_port
      self.ss = smtplib.SMTP_SSL(self.host, self.port)
      self.ss.ehlo()
      sender_addr = '____________@naver.com'   # 나의 네이버 메일 주소 입력
      mail_pwd = ''                            # 나의 메일 접속 비번 입력 (메일접속이 2단계 인증으로 되어 있으면 메일접속 안 됨)
      self.ss.login(sender_addr,mail_pwd)
  
  def send_message(self,mail_content,sender_addr,receiver_addr):
      for i in range(len(receiver_addr)):
          cc = mail_content.get_message(sender_addr,receiver_addr[i])
          self.ss.send_message(cc,from_addr=sender_addr,to_addrs=receiver_addr[i])
          print('메일송부완료주소[{}] : {}'.format(i,receiver_addr[i]))               # 메일송부완료되면 출력됨
      del cc

# 메일송부 종합정보 입력
subject = ''                  # 메일 제목 입력
attach_file_name = ''         # 메일내 첨부파일명 입력 (압축본이 좋음 aaa.zip, But 용량크면 전송실패할 수도 있음)

# 메일 안에 적을 내용 입력하기
template = Template("""
                    <html>
                          <head></head>
                          <body>
                              ${NAME}!<br>
                              필요한 메일내용을 여기에 입력하세요.<br>
                              <br>
                          </body>
                    </html>
                    """)
template_params = {'NAME':'[mailing]'}
mail_contents   = EmailHTMLImageContent(subject, attach_file_name, template, template_params)
sender_addr     = formataddr((str(Header('일반발신','utf-8')),'_________@naver.com'))     # 보낸사람 -> 나의 메일 주소 입력
mail_list       = pd.read_excel('mail_address_list_private.xlsx',index_col = 0)          # 수신자 테이블 불러오기 (별도엑셀양식 참조) -> 수신자 메일주소 입력해놔야 함
receiver_addr   = mail_list.iloc[:,1].tolist()                                           # 수신자 주소 리스트화
mail_engine_start = EmailSender()
mail_engine_start.send_message(mail_contents, sender_addr, receiver_addr)



