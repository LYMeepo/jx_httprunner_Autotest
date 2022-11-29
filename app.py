import time

from flask import Flask, render_template, request
import subprocess, os, shutil
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__, template_folder='templates', static_folder='static')
# apps.config['UPLOAD_FOLDER'] = 'files'
log = ""
reports_dir = os.sep.join(['templates', 'reports'])
executor = ThreadPoolExecutor(1)


@app.route('/')
def index():
    return render_template(r'index.html')


@app.route('/hruntest', methods=["GET"])
def hruntest():
    templateData = {"envs": get_envs()
                    }

    return render_template(r'hruntest.html', **templateData)


@app.route('/hruntest_success', methods=["POST"])
def hruntest_success():
    sel_env = request.form.get('sel_env')
    switch_env(sel_env)
    time.sleep(1)
    hrun_start(sel_env)
    return render_template(r'hruntest_success.html')


@app.route('/log')
def log():
    templateData = {'log': log
                    }
    return render_template(r'log.html', **templateData)


@app.route('/reports', methods=["GET", "POST"])
def reports():
    reports = []
    for file_name in os.listdir(reports_dir):
        reports.append(file_name)

    templateData = {"reports": reports
                    }
    return render_template(r'reports.html', **templateData)


@app.route('/report', methods=["GET", "POST"])
def report():
    btn = request.form.get('btn')
    return render_template(r'reports/' + btn)


@app.route('/env_manager', methods=["GET"])
def env_manager():
    return render_template(r'env_manager.html')


@app.route('/addenv', methods=["GET"])
def addenv():
    return render_template(r'addenv.html')


@app.route('/addenv_success', methods=["POST"])
def addenv_success():
    env_name = request.form.get('env_name')
    env_content = request.form.get('env_content')
    add_env_file(env_content, env_name)

    return render_template(r'addenv_success.html')

@app.route('/delete_env', methods=["GET"])
def delete_env():
    templateData = {"envs": get_envs()
                    }
    return render_template(r'delete_env.html',**templateData)


@app.route('/delete_env_success', methods=["POST"])
def delete_env_success():
    env_name = request.form.get('sel_env')
    delete_env_file(env_name)
    return render_template(r'delete_env_success.html')


@app.route('/env_detail_sel', methods=["GET"])
def env_detail_sel():
    templateData = {"envs": get_envs()
                    }
    return render_template(r'env_detail_sel.html',**templateData)


@app.route('/env_detail', methods=["POST"])
def env_detail():
    sel_env = request.form.get('sel_env')
    env_detail_str = get_env_detail(sel_env)
    templateData = {"env_detail_str": env_detail_str
                    }

    return render_template(r'env_detail.html', **templateData)


# 添加环境配置文件
def add_env_file(env_content, env_name):
    env = os.sep.join(['env', env_name + ".env"])
    with open(env, 'w', newline='') as f:
        f.write(env_content)


def delete_env_file(env_name):
    env_file_src = os.sep.join(['env', env_name])
    if os.path.exists(env_file_src):
        os.remove(env_file_src)


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


# 加载日志
def load_log():
    global log
    while (True):
        with open("httprunner.log", 'r') as f:
            log = f.read()
            log = log.replace('\n','')
        time.sleep(3)


# 执行自动化
def hrun_start(env_name):
    env_name_str = os.path.splitext(env_name)[0]
    testsuites = os.sep.join(['testsuites', 'testsuite.yml'])
    save_report = os.sep.join([reports_dir, env_name_str + '_' + get_now_time() + ".html"])
    command = "hrun " + testsuites + " --report-file " + save_report + "" " > httprunner.log"
    subprocess.Popen(command, shell=True,
                     stdout=subprocess.PIPE)
#获取当前时间
def get_now_time():
    return time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())

if __name__ == '__main__':
    init_log_file()
    app.run(host="0.0.0.0", port=13243)
