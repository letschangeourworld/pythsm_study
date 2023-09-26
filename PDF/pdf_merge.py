# installation -> pip install pypdf[full]

import os
from pypdf import PdfWriter

# to create a list of pdf files in a directory
path = './pdf_files/'
dir_lst = os.listdir(path)

# To activate the instance of a pypdf class
merger = PdfWriter()

for p in dir_lst:
  # to create the object of a pdf file
  file = open('./Pdf_files/' + p, 'rb')
  # to gather each object in merger function
  merger.append(file)
  
  # another function 1
  # 2페이지 다음페이지에 pdf file을 집어넣는데, file의 1페이지만 사용
  # merger.merge(position = 2, fileobj = file, page = (0, 1))

  # another function 2
  # pdf file의 3페이지를 더해넣기
  # merger.append(fileobj = file, page=(0, 3))

# to save the merged pdf files and create the object of a merged file again
output = open('ppp_merged.pdf', 'wb')
merger.write(output)

# close the merger function and the output object
merger.close()
output.close()

