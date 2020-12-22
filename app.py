import csv
import os
import queue
import pandas as pd

from flask import Flask, request, render_template, redirect, url_for
from flask_apscheduler import APScheduler
from flask_redis import FlaskRedis

from src.lib.spider.base_spider import SPIDER_NAME
from src.lib.spider.xiaoqu_spider import XiaoQuBaseSpider
from src.lib.spider.ershou_spider import ErShouSpider
from src.lib.spider.zufang_spider import ZuFangBaseSpider
from src.lib.spider.loupan_spider import LouPanBaseSpider
from src.lib.utility.date import get_date_string
from src.lib.utility.path import DATA_PATH
from src.xiaoqu_to_csv import xiaoqu_to_csv

queues = queue.Queue()


class Config(object):  # 创建配置，用类
    # 任务列表
    JOBS = [
        # {  # 第一个任务
        #     'id': 'job1',
        #     'func': '__main__:job_1',
        #     'args': (1, 2),
        #     'trigger': 'cron', # cron表示定时任务
        #     'hour': 19,
        #     'minute': 27
        # },
        {  # 第二个任务，每隔5S执行一次
            'id': 'job1',
            'func': '__main__:run_spider',  # 方法名
            'args': (queues,),  # 入参
            'trigger': 'interval',  # interval表示循环任务
            'seconds': 30,
        },
    ]
    REDIS_URL = "redis://:Xu551212@119.8.116.167/0"


app = Flask(__name__)
app.config.from_object(Config())
redis_client = FlaskRedis(app, decode_responses=True)


@app.route('/')
def index():
    cities = {
        'bj': '北京',
        'cd': '成都',
        'cq': '重庆',
        'cs': '长沙',
        'dg': '东莞',
        'dl': '大连',
        'fs': '佛山',
        'gz': '广州',
        'hz': '杭州',
        'hf': '合肥',
        'jn': '济南',
        'nj': '南京',
        'qd': '青岛',
        'sh': '上海',
        'sz': '深圳',
        'su': '苏州',
        'sy': '沈阳',
        'tj': '天津',
        'wh': '武汉',
        'xm': '厦门',
        'yt': '烟台',
    }
    house_type = {
        "xiaoqu": "小区房价",
        "ershou": "挂牌二手房",
        "zufang": "出租房",
        "loupan": "新房",
    }
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
        "cities": cities,
        "house_type": house_type,
        "crawl_status": crawl_status,
        "crawl_tasks": crawl_tasks,
    }
    return render_template('index_2.html', **content)


@app.route('/delete')
def delete():
    request_param = request.values.to_dict()
    redis_client.hdel('crawl_task', request_param['city'] + '_' + request_param['house_type'])
    return redirect(url_for('index'))


@app.route('/result')
def result():
    request_param = request.values.to_dict()
    date = get_date_string()
    csv_dir = "{0}/{1}/{2}/{3}/{4}".format(DATA_PATH, SPIDER_NAME, request_param['house_type'], request_param['city'], date)
    csv_path = csv_dir + "{}_{}.csv".format(request_param['house_type'], request_param['city'])
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
            }
        except Exception as e:
            app.logger.error(e)
            content = dict()
    else:
        content = dict()
    return render_template('index.html', **content)


@app.route('/test', methods=['POST'])
def hello_world():
    request_param = request.values.to_dict()
    if all(i in request_param for i in ('city', 'house_type')) and all((request_param['city'], request_param['house_type'])):
        app.logger.info("获取到 city {}, house_type {}".format(request_param['city'], request_param['house_type']))
        redis_client.hset('crawl_task', request_param['city']+'_'+request_param['house_type'], 1)
        queues.put((request_param['city'], request_param['house_type']))
        app.logger.info("已推到队列！！！")
    else:
        return "parameter error!!!"
    return "Ready to grab!!!"


def run_spider(queues):
    app.logger.info('在循环队列')
    while True:
        try:
            data = queues.get(timeout=10)
        except:
            app.logger.info('队列是空的')
            break
        redis_client.hset('crawl_task', data[0] + '_' + data[1], 2)
        date = get_date_string()
        csv_dir = "{0}/{1}/{2}/{3}/{4}".format(DATA_PATH, SPIDER_NAME, data[1], data[0], date)
        csv_path = csv_dir + "{}_{}.csv".format(data[1], data[0])
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


if __name__ == '__main__':
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    app.run(debug=True)
