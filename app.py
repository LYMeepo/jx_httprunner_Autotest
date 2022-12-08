import time

from flask import Flask, render_template, request
import subprocess, os, shutil, zipfile
from concurrent.futures import ThreadPoolExecutor


template_folder = os.getcwd() + '/templates'
static_folder = os.getcwd() + '/static'
static_url_path = '/static'

app = Flask(__name__, template_folder=template_folder, static_folder=static_folder,static_url_path=static_url_path)
app.config['UPLOAD_FOLDER'] = 'cases_bak'

log = ""
reports_dir = os.sep.join(['templates', 'reports'])
executor = ThreadPoolExecutor(1)
path = ""
api_path = "api"


@app.route('/')
def index():
    global api_path
    api_path = "api"
    templateData = {"path": path}
    return render_template(r'index.html', **templateData)


@app.route('/hruntest', methods=["GET"])
def hruntest():
    global api_path
    api_path = "api"
    templateData = {"path": path,
                    "envs": get_envs(),
                    "cases": get_cases()}

    return render_template(r'hruntest.html', **templateData)


@app.route('/hruntest_success', methods=["POST"])
def hruntest_success():
    templateData = {"path": path,
                    "clew": "执行成功"}

    sel_cases = request.form.get('sel_cases')
    sel_env = request.form.get('sel_env')

    switch_cases(sel_cases)
    switch_env(sel_env)

    time.sleep(1)
    hrun_start(sel_env)
    return render_template(r'success.html', **templateData)


@app.route('/log')
def log():
    global api_path
    api_path = "api"
    templateData = {'log': log,
                    "path": path
                    }
    return render_template(r'log.html', **templateData)

# 切换测试用例集合
def switch_cases(sel_cases):
    #移除api、testcases、testsuites
    shutil.rmtree("api")
    shutil.rmtree("testcases")
    shutil.rmtree("testsuites")

    #从cases_bak复制api、testcases、testsuites、debugtalk.py
    api_dir = os.sep.join(['cases_bak',sel_cases,'api'])
    testcases_dir = os.sep.join(['cases_bak', sel_cases, 'testcases'])
    testsuites_dir = os.sep.join(['cases_bak', sel_cases, 'testsuites'])
    debugtalk_dir = os.sep.join(['cases_bak', sel_cases, 'debugtalk.py'])
    shutil.copytree(api_dir, r"api")
    shutil.copytree(testcases_dir, r"testcases")
    shutil.copytree(testsuites_dir, r"testsuites")
    shutil.copyfile(debugtalk_dir, 'debugtalk.py')


#========================测试报告============================
@app.route('/reports', methods=["GET", "POST"])
def reports():
    global api_path
    api_path = "api"
    reports = []
    for file_name in os.listdir(reports_dir):
        reports.append(file_name)

    templateData = {"reports": reports,
                    "path": path
                    }
    return render_template(r'reports.html', **templateData)


@app.route('/report', methods=["GET", "POST"])
def report():
    btn = request.form.get('btn')
    templateData = {"path": path}
    return render_template(r'reports/' + btn, **templateData)
#========================测试报告============================

#========================配置管理============================
@app.route('/env_manager', methods=["GET"])
def env_manager():
    global api_path
    api_path = "api"
    templateData = {"path": path}
    return render_template(r'env_manager.html', **templateData)


@app.route('/addenv', methods=["GET"])
def addenv():
    templateData = {"path": path}
    return render_template(r'addenv.html', **templateData)


@app.route('/addenv_success', methods=["POST"])
def addenv_success():
    templateData = {"path": path,
                    "clew": "添加成功"}
    env_name = request.form.get('env_name')
    env_content = request.form.get('env_content')
    add_env_file(env_content, env_name)

    return render_template(r'success.html', **templateData)


@app.route('/delete_env', methods=["GET"])
def delete_env():
    templateData = {"envs": get_envs(),
                    "path": path
                    }
    return render_template(r'delete_env.html', **templateData)


@app.route('/delete_env_success', methods=["POST"])
def delete_env_success():
    templateData = {"path": path,
                    "clew": "删除成功"}
    env_name = request.form.get('sel_env')
    delete_env_file(env_name)
    return render_template(r'success.html', **templateData)


@app.route('/env_detail_sel', methods=["GET"])
def env_detail_sel():
    templateData = {"envs": get_envs(),
                    "path": path
                    }
    return render_template(r'env_detail_sel.html', **templateData)


@app.route('/env_detail', methods=["POST"])
def env_detail():
    sel_env = request.form.get('sel_env')
    env_detail_str = get_env_detail(sel_env)
    templateData = {"env_detail_str": env_detail_str,
                    "path": path
                    }

    return render_template(r'env_detail.html', **templateData)


# 添加环境配置文件
def add_env_file(env_content, env_name):
    env = os.sep.join(['env', env_name + ".env"])
    with open(env, 'w', newline='') as f:
        f.write(env_content)

# 删除文件夹
def delete_dir(dir_name):
    env_file_src = os.sep.join(['cases_bak', dir_name])
    if os.path.exists(env_file_src):
        shutil.rmtree(env_file_src)

# 删除文件
def delete_env_file(env_name):
    env_file_src = os.sep.join(['env', env_name])
    if os.path.exists(env_file_src):
        os.remove(env_file_src)
#========================配置管理============================

#========================用例管理============================
@app.route('/case_manager', methods=["GET"])
def case_manager():
    global api_path
    api_path = "api"
    templateData = {"path": path}
    return render_template(r'cases/case_manager.html', **templateData)

@app.route('/api_add', methods=["GET"])
def api_add():
    templateData = {"path": path}

    return render_template(r'cases/api_add.html', **templateData)

@app.route('/api_add_success', methods=["POST"])
def api_add_success():
    templateData = {"path": path,
                    "clew": "添加成功"}
    # 保存压缩文件到cases_bak
    file = request.files['file']
    save_path = os.path.join(app.config['UPLOAD_FOLDER'])
    save_path = os.sep.join([save_path, r"cases.zip"])
    file.save(save_path)
    # 解压压缩文件
    api_dir = os.sep.join(["cases_bak"])
    zf = zipfile.ZipFile(save_path)
    zf.extractall(path=api_dir)

    return render_template(r'success.html', **templateData)


@app.route('/api_del', methods=["GET"])
def api_del():
    templateData = {"path": path,
                    "cases": get_cases()}
    return render_template(r'cases/api_del.html', **templateData)

@app.route('/api_del_success', methods=["POST"])
def api_del_success():
    templateData = {"path": path,
                    "clew": "删除成功"}
    sel_cases = request.form.get('sel_cases')
    delete_dir(sel_cases)
    return render_template(r'success.html', **templateData)

#========================用例管理============================

# 初始化日志文件
def init_log_file():
    with open("httprunner.log", 'w') as f:
        f.write("等待任务中。。。")
    executor.submit(load_log)


# 切换环境配置文件
def switch_env(sel_env):
    env = os.sep.join(['env', sel_env])
    shutil.copy(env, ".env")  # 复制文件


# 获取配置文件列表
def get_envs():
    for _, _, envs in os.walk("env"):
        return envs


# 获取配置文件详情
def get_env_detail(env_name):
    env_detail_str = ""
    env = os.sep.join(['env', env_name])
    with open(env, 'r') as f:
        env_detail_str = f.read()
    return env_detail_str

# 获取api
def get_cases():
    for _, api_dirs, _ in os.walk("cases_bak"):
        return api_dirs

# 加载日志
def load_log():
    global log
    while (True):
        with open("httprunner.log", 'r') as f:
            log = f.read()
        time.sleep(3)


# 执行自动化
def hrun_start(env_name):
    env_name_str = os.path.splitext(env_name)[0]
    testsuites = os.sep.join(['testsuites', 'testsuite.yml'])
    save_report = os.sep.join([reports_dir, env_name_str + '_' + get_now_time() + ".html"])
    command = "hrun " + testsuites + " --report-file " + save_report + "" " > httprunner.log"
    subprocess.Popen(command, shell=True,
                     stdout=subprocess.PIPE)


# 获取当前时间
def get_now_time():
    return time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())

if __name__ == '__main__':

    init_log_file()
    app.run(host="0.0.0.0", port=80)
