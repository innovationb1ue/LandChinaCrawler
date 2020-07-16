import csv

def save_exception(e:Exception):
    with open('./Exceptions.txt', 'a') as f:
        f.write(str(e))
        f.write('\n')


def save_log_string(string:str):
        with open('./Exceptions.txt', 'a') as f:
            f.write(str(string))
            f.write('\n')


def save(infos:list, filepath:str) -> None:
    try:
        with open(filepath, 'a', encoding='gb2312', newline='', errors='ignore') as f:
            writer = csv.writer(f)
            writer.writerow(infos)
    except Exception as e:
        save_exception(e)

# not used
def save_html(content:str, filepath):
    try:
        with open(filepath, 'a', encoding='gb2312', errors='ignore') as f:
            f.write(content)
    except Exception as e:
        save_exception(e)
        save_log_string('Error in save_html')
    