# __author__ = 'wilsonLwx'
# __date__ = '2019/3/6'
import csv


def write_csv(dict_, file_name):
    # 写入csv 文件的方法
    with open(file_name, 'a+') as f:
        f.seek(0, 0)
        content = f.readline().replace('\n', '')
        title_list = content.split(',')
        cw = csv.DictWriter(f, list(dict_.keys()))
        if list(dict_.keys()) != title_list:
            # 判断文件内是否已经有title 没有就先写入title
            cw.writeheader()
            cw.writerow(dict_)
        else:
            # 如果已经有title 就直接写入数据
            cw.writerow(dict_)


def read_csv(file_name):
    with open(file_name, encoding='utf-8') as f:
        content = csv.reader(f)
        new_list = []
        for i in content:
            new_list.append(''.join(i))
        return new_list
