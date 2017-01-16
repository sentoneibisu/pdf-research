import pandas as pd

df_sample =\
pd.DataFrame([["day1","day2","day1","day2","day1","day2"],
              ["A","B","A","B","C","C"],
              [100,150,200,150,100,50],
              [120,160,100,180,110,80]]).T
df_sample.columns = ["day_no","class","score1","score2"]
df_sample.index = [11,12,13,14,15,16]
print df_sample
