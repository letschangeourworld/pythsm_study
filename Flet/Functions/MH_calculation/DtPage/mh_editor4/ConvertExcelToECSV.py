
import os
import pandas as pd

df_shtnm_lst = pd.ExcelFile("mh_instruction_sheet_modified.xlsx").sheet_names

for i in range(len(df_shtnm_lst)):
    df = pd.read_excel("mh_instruction_sheet_modified.xlsx",
                       sheet_name = df_shtnm_lst[i],
                       header = 1, index_col = None)
    df2 = df.iloc[:27,2:]
    df3 = df2.fillna("")
    df4 = df3[df3.iloc[:,6] != ""]
    if i+1 >= 10:
        df4.to_csv(f"csv_files_instructions/[{i+1}] {df_shtnm_lst[i]}.csv", index = False, encoding = "utf-8-sig")
    else:
        df4.to_csv(f"csv_files_instructions/[0{i+1}] {df_shtnm_lst[i]}.csv", index = False, encoding = "utf-8-sig")        

