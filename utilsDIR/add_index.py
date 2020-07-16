#encoding=gb2312
import csv
def add_index(filename):
    index = 0
    with open(filename, 'r', encoding='gb2312', errors='ignore', newline='') as f:
        with open('../Data/indexed-出让公告.csv', 'a', encoding='gb2312', errors='ignore', newline='') as f1:
            reader = csv.reader(f)
            writer = csv.writer(f1)
            for row in reader:
                row = [index] + row
                writer.writerow(row)
                index += 1
    print('finished indexing')

if __name__ == '__main__':
    add_index('../Data/出让公告.csv')