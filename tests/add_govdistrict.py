import csv
import gc

with open('./市场交易-土地转让_detail.csv', encoding='gb2312', mode='r') as f:
    reader =csv.reader(f)
    data = [*reader]
titles = data[0]
titles.append('行政区')
data = data[1:]

with open('./indexed-土地转让.csv', encoding='gb2312', mode='r') as f:
    reader = csv.reader(f)
    data_list = [*reader][1:]

locdict = {}
for row in data_list:
    locdict[row[0]] = row[1]


finaldata = []
for row in data:
    district = locdict[row[0]]
    row.append(district)
    finaldata.append(row)

with open('./市场交易-土地转让_detail_2.csv', 'a', encoding='gb2312', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(titles)
    for i in finaldata:
        writer.writerow(i)
    




