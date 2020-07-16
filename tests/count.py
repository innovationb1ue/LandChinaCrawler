#encoding=gb2312
import csv
count = 0
with open('../市场交易-土地转让_detail.csv', encoding='gb2312', mode='r') as f:
    reader = csv.reader(f)
    for row in f:
        count += 1

print(count)

