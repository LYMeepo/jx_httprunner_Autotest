import os
import shutil
import platform
import json
import yaml

def har_to_yml(oldHar):
    with open(oldHar,'rb') as f:
        #获取文件名
        har_str = f.readlines()[0]
        har_json = json.loads(har_str)
        method = har_json["log"]["entries"][0]["request"]["method"]
        url = har_json["log"]["entries"][0]["request"]["url"]
        index1,index2 = 0,0
        file_name = ""

        if method == "POST":
            index1 = url.find("10250")
            file_name = url[index1 + 5:]
        if method == "GET":
            index1 = url.find("10250")
            if "?" in url:
                index2 = url.find("?")
            else:
                index2 = len(url)
            file_name = url[index1 + 5 : index2]
        print("---------:",file_name)
        file_name = file_name.replace("/","_")
        file_name = file_name[1:]
        print(file_name)
        newHar = "har\\" + file_name + ".har"
        shutil.copy(oldHar, newHar)

        if platform.system() == "Windows":
            new_yml = r"script\\old_yml\\" + file_name + ".yml"
            dos = "har2case " + newHar + " -2y "
            old_yml = r"har\\" + file_name + ".yml"

            os.system(dos)
            shutil.move(old_yml, new_yml)
            edit_yml(new_yml)


        if platform.system() == "Linux":
            print('Linux系统')

def edit_yml(file):
    with open(file, 'r', encoding="utf_8") as f:
        old_yml = yaml.load(f)
    api = old_yml["teststeps"][0]
    api["request"]["headers"]["Authorization"] = "$token"
    api["request"]["headers"].pop("User-Agent")
    api["base_url"] = "${ENV(base_url)}"
    api["request"]["url"] = api["name"]
    with open(file, 'w', encoding='utf-8') as fw:
        yaml.dump(api,fw)



def walk_file(file):
    for root, dirs, files in os.walk(file):
        # root 表示当前正在访问的文件夹路径
        # dirs 表示该文件夹下的子目录名list
        # files 表示该文件夹下的文件list
        # 遍历文件
        for f in files:
            oldHar = os.path.join(root, f)
            har_to_yml(oldHar)

def main():
    walk_file(r"script\old_har")


if __name__ == '__main__':
    main()