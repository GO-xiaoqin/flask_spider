import csv
import json
import os
import queue

from flask import Flask, request, render_template, redirect, url_for, send_file
from flask_apscheduler import APScheduler
from flask_redis import FlaskRedis

from src.lib.spider.base_spider import SPIDER_NAME
from src.lib.spider.xiaoqu_spider import XiaoQuBaseSpider
from src.lib.spider.ershou_spider import ErShouSpider
from src.lib.spider.zufang_spider import ZuFangBaseSpider
from src.lib.spider.loupan_spider import LouPanBaseSpider
from src.lib.utility.date import get_date_string
from src.lib.utility.db_pool import get_area_city
from src.lib.utility.path import DATA_PATH
from src.xiaoqu_to_csv import xiaoqu_to_csv
from logging.config import dictConfig


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format':  "[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s][%(thread)d] - %(message)s",
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


queues = queue.Queue()


class Config(object):  # 创建配置，用类
    JOBS = [
        {  # 每隔5S执行一次
            'id': 'job1',
            'func': '__main__:run_spider',  # 方法名
            'args': (queues,),  # 入参
            'trigger': 'interval',  # interval表示循环任务
            'seconds': 30,
        },
    ]
    REDIS_URL = "redis://:Xu551212@127.0.0.1/0"


app = Flask(__name__)
app.config.from_object(Config())
redis_client = FlaskRedis(app, decode_responses=True)


@app.route('/')
def index():
    # TODO 进行前端参数传递
    crawl_status = {
        '1': '待抓取',
        '2': '抓取中',
        '3': '抓取完成',
        '4': '抓取失败',
    }

    crawl_task = redis_client.hgetall('crawl_task')
    crawl_tasks = list()
    for task in crawl_task:
        crawl_tasks.append((
            str(task).split('_')[0],
            str(task).split('_')[1],
            str(crawl_task[task]),
        ))
    content = {
        "crawl_status": crawl_status,
        "crawl_tasks": crawl_tasks,
    }
    return render_template('index.html', **content)


@app.route('/delete')
def delete():
    request_param = request.values.to_dict()
    redis_client.hdel('crawl_task', request_param['city'] + '_' + request_param['house_type'])
    return redirect(url_for('index'))


@app.route('/result')
def result():
    request_param = request.values.to_dict()
    csv_path = get_csv_dir((request_param['city'], request_param['house_type']))
    app.logger.info(csv_path)
    if os.path.exists(csv_path):
        try:
            contents = list()
            with open(csv_path) as csvfile:
                csv_reader = csv.reader(csvfile)  # 使用csv.reader读取csvfile中的文件
                birth_header = next(csv_reader)  # 读取第一行每一列的标题
                for row in csv_reader:  # 将csv 文件中的数据保存到birth_data中
                    contents.append(row)
            cont = [i[0].split(';') for i in contents]
            header = birth_header[0].split(';')
            content = {
                "contents": cont[:50],
                "header": header,
                "request_param": request_param,
            }
        except Exception as e:
            app.logger.error(e)
            content = dict()
    else:
        content = dict()
    return render_template('result.html', **content)


@app.route('/download')
def download_file():
    request_param = request.values.to_dict()
    csv_path = get_csv_dir((request_param['city'], request_param['house_type']))
    file_name = get_date_string() + "{}_{}.csv".format(request_param['house_type'], request_param['city'])

    return send_file(csv_path, mimetype='text/csv', attachment_filename=file_name, as_attachment=True)


@app.route('/grab', methods=['POST'])
def grab():
    request_param = request.values.to_dict()
    if all(i in request_param for i in ('city', 'house_type')) and all((request_param['city'], request_param['house_type'])):
        app.logger.info("获取到 city {}, house_type {}".format(request_param['city'], request_param['house_type']))
        redis_client.hset('crawl_task', request_param['city']+'_'+request_param['house_type'], 1)
        queues.put((request_param['city'], request_param['house_type']))
        app.logger.info("已推到队列！！！")
    else:
        return json.dumps({'status': "0", "result": "parameter error!!!"})
    return json.dumps({'status': "1", "result": "Ready to grab!!!"})


@app.route('/get_city', methods=['GET'])
def get_city():
    result = get_area_city()
    if result:
        return json.dumps({'status': 1, "result": result})
    return json.dumps({'status': 0, "result": None})


def run_spider(queues):
    app.logger.info('在循环队列')
    while True:
        try:
            data = queues.get(timeout=10)
        except Exception:
            app.logger.info('队列是空的')
            break
        redis_client.hset('crawl_task', data[0] + '_' + data[1], 2)
        csv_path = get_csv_dir(data)
        if not os.path.exists(csv_path):
            try:
                if data[1] == 'xiaoqu':
                    XiaoQuBaseSpider().start(data[0])
                else:
                    redis_client.hset('crawl_task', data[0] + '_' + data[1], 3)
                    continue
                # elif data[1] == 'ershou':
                #     ErShouSpider().start(data[0])
                # elif data[1] == 'zufang':
                #     ZuFangBaseSpider().start(data[0])
                # elif data[1] == 'loupan':
                #     LouPanBaseSpider().start(data[0])
                xiaoqu_to_csv(data)
                redis_client.hset('crawl_task', data[0] + '_' + data[1], 3)
            except Exception as e:
                redis_client.hset('crawl_task', data[0] + '_' + data[1], 4)
                app.logger.error(e)
        else:
            redis_client.hset('crawl_task', data[0] + '_' + data[1], 3)
            app.logger.info("已经抓过。")


def get_csv_dir(data):
    date = get_date_string()
    csv_dir = "{0}/{1}/{2}/{3}/{4}".format(DATA_PATH, SPIDER_NAME, data[1], data[0], date)
    csv_path = csv_dir + "{}_{}.csv".format(data[1], data[0])

    return csv_path


if __name__ == '__main__':
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    app.run(host='0.0.0.0', port=8883, debug=True)
