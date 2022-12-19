import csv
import pandas
import datetime
import os
import pathlib

class CSVIO:

    DATAS_PATH = './datas'
    DATAS_EXTENTION = '.csv'

    def __init__(self):
        pass

    def readFileDict(self, title:str):
        file_path = f"{self.DATAS_PATH}/{title}{self.DATAS_EXTENTION}"
        if not os.path.isfile(file_path): return []
        df = pandas.read_csv(file_path)
        datas = df.to_dict('records')
        return datas
    
    def readFileList(self, title:str):
        file_path = f"{self.DATAS_PATH}/{title}{self.DATAS_EXTENTION}"
        if not os.path.isfile(file_path): return []
        with open(file_path, 'r') as input_file:
            #data = list(csv.reader(input_file, delimiter="\n"))
            data = []
            while (line := input_file.readline().rstrip()):
                data.append(line)

        input_file.close()
        return data

    def writeFile(self, title:str, datas:dict):
        file_path = f"{self.DATAS_PATH}/{title}{self.DATAS_EXTENTION}"

        # check if the report file already exists
        if os.path.isfile(file_path):
            print(f'file {title} already exists')
            #return
        
        keys = datas[0].keys()

        #print(pathlib.Path().resolve())

        with open(file_path, 'w', newline='') as output_file:
            fc = csv.DictWriter(output_file, keys)
            fc.writeheader()
            fc.writerows(datas)
        output_file.close()
    
    def writeList(self, title:str, datas:list):
        file_path = f"{self.DATAS_PATH}/{title}{self.DATAS_EXTENTION}"

        with open(file_path, 'w', newline='') as output_file:
            for line in datas:
                output_file.write(("%s\n" % line))
        output_file.close()
    
    def isFilePresent(self, title:str):
        file_path = f"{self.DATAS_PATH}/{title}{self.DATAS_EXTENTION}"

        if os.path.isfile(file_path): return True
        else: return False


def main():
    print('test CSV')
    io = CSVIO()
    data1 = io.readFile('csv_test')
    print(data1)
    print(data1[1]['col3'])
    data1[1]['col3'] = 'bob'
    data2 = [{'col10':'bob', 'col20':'33', 'col30':'24.55'},
             {'col10':'bobette', 'col20':'36', 'col30':'55.24'}]
    io.writeFile('csv_test', data1)
    io.writeFile('csv_test2', data1)
    io.writeFile('csv_test3', data2)

    data3 = [{'excluded':'test1'}, {'excluded':'test2'}, {'excluded':'test3'}]
    io.writeFile('csv_test4', data3)




if __name__ == '__main__': main()
