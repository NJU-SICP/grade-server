# Grader Server

本项目是NJU-SICP课程使用的基于Flask的测评后端。其使用场景为：

- 学生使用我们提供的`submit.py`脚本把作业文件提交到这个测评后端中。
- 测评后端使用docker容器来构建虚拟环境对学生提交的作业文件进行测试。测试完成后销毁容器，并把结果返回给学生。
- 同时，学生还能通过网页端来查询自己提交作业的成绩。

## 部署

首先确保服务器上Python的版本大于3.6。然后进入项目的根目录，创建virtual environment：

    $ python -m venv venv
    $ source venv/bin/activate


接着安装依赖

    $ pip install -r requirements.txt

接下来，我们准备Flask环境变量：

    $ export FLASK_ENV=production
    $ export FLASK_APP=grade-server.py

现在grade-server已经准备就绪了。不过在运行之前，我们要初始化数据库：

    $ flask init-db

最后，使用gunicorn运行grade-server：

    gunicorn -w <worker_num> -b 0.0.0.0:5000 grade-server:app

## 学生导入

刚初始的数据库还是空的。首先我们会关注如何限制哪些学生能提交作业。为此，我们提供了学生导入的功能。你可以通过

    flask import-students <FILE>

来从某个包含学生名单的`FILE`中导入学生。`FILE`为CSV文件，每行的格式为

    <stuid>,<stuname>

即第一列为学生学号，第二列为学生姓名。

对应的，学生在提交作业的时候需要指定学号和姓名。作业提交脚本的样例为`client/submit.py`，其基本使用方法为：

    python submit.py --stuid <STUID> --stuname <STUNAME>

## 添加作业

接下来，我们来看如何添加作业。

假设你想给学生布置的作业名字叫做`project1`。很自然的，你会创建一个目录`project1`，把作业文件都放在这个目录下面，然后发给学生。学生需要修改其中一些文件来完成`project1`要求的编程作业。最终学生需要提交他的修改的文件给服务器评分。

假设学生修改并将要提交的文件为`codeA.py`,`codeB.py`。你显然需要把学生的这些文件放到某个测试环境中，然后运行某个指令评分。我们的后端假设你的测试环境是某个docker image，测试指令为docker image的CMD。所以你需要自己创建一个docker image作为测试环境。然后通过作业配置文件告诉我们的后端。

当学生把文件提交过来后，我们的后端主要会做六件事情：

1. 检查DDL。如果超过DDL，则拒绝评测。
2. 从你提供的image开始创建一个容器。
3. 把学生的文件复制到容器内部，路径需要你指定。
4. 运行容器进行测试。
5. 获得容器中的结果，计算学生的分数。
6. 把学生的分数保存到数据库内，然后回显信息给学生。

综合上面的使用场景，我们的作业配置文件参考格式如下：

```js
{
    "name": "project1", // 作业名称
    "grader_image": "sicp-project1-env", // 你制作的测试环境image
    "required_files": [
        {
            "filename": "codeA.py", // 提交的作业文件
            "container_path": "/usr/src/project1" // 拷贝到的容器中的目标路径
        },
        {
            "filename": "codeB.py",
            "container_path": "/usr/src/project1"
        },
    ],
    "ddl": "2020-12-31 16:10:00", // DDL
    "timeout": 15, // 设置容器运行超时为15秒
    "score_extractor": "random_extractor" // 分数提取函数
}
```

其中可能有点不那么好理解的是`"score_extractor"`属性。先前我们提到，我们的后端会从容器的输出中计算学生的分数。因为我们预先不知道你的测试脚本会输出什么字符串，所以你需要提供一个解析这个字符串计算学生分数的函数。这个函数就叫做`score_extractor`。

你可以在`config.py`中定义你作业的`score_extractor`，然后给它起一个名字形成键值对添加到`config.py`的`score_extractors`变量中。上面配置文件中`"score_extractor"`的值就是你起的那个名字。

当你编写好这个作业的配置文件后，不妨给它命名为`proj1.json`，然后可以使用

    flask import-assignmet proj1.json

把这次作业添加grade-server中。

最后你需要按照`client/submit.py`的样例修改提交脚本中作业名`aname`和需要提交的文件`files`。

## DDL宽限期

我们的后端可以允许学生在DDL后一段宽限期内补交作业，但是会对作业分数打一些折扣。你可以通过修改`config.py`中`Config`类的`GRACE_PERIOD`属性修改宽限期（默认1天），通过`GRACE_PERIOD_PENALTY`属性修改惩罚系数（默认扣掉30%的分数）。

## 运维

`gunicorn`通过`-D`参数在后台运行时并不太容易停止、重启、查看日志。所以我们需要一个工具来管理`gunicorn`。

我们推荐使用`supervisor`。Ubuntu上使用

    $ sudo apt install supervisor

安装。然后在`/etc/supervisor/conf.d`下按如下参考添加配置文件`web.conf`：

    [program:grade-server]
    command=/path/to/grade-server/venv/bin/gunicorn -w 32 -b 0.0.0.0:5000 grade-server:app
    directory=/path/to/grade-server
    autostart=true
    autorestart=true
    stdout_logfile=/path/to/grade-server/log/gunicorn.log
    stderr_logfile=/path/to/grade-server/log/gunicorn.err
    environment=APP_CONFIG="production",SECRET_KEY="hard to guess string"

最后使用

    $ sudo supervisorctl upgrade
    $ sudo supervisorctl start grade-server

就可以启动了