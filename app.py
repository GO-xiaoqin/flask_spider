import csv
import json
import queue

from flask import Flask, request, render_template, redirect, url_for, send_file
from flask_apscheduler import APScheduler
from flask_redis import FlaskRedis

from src.lib.spider.xiaoqu_spider_db import XiaoQuBaseSpider
from src.lib.spider.ershou_spider_db import ErShouSpider
from src.lib.spider.loupan_spider_db import LouPanBaseSpider
from src.lib.utility.date import get_date_string
from src.lib.utility.db_pool import get_area_city, get_crawl_task, insert_crawl_task, get_db_city, get_info, \
    get_xiaou_detail
from src.lib.utility.path import DATA_PATH
from conf import *
from logging.config import dictConfig


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format':  "[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s]-%(message)s",
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
    REDIS_URL = REDIS_URL


app = Flask(__name__)
app.config.from_object(Config())
redis_client = FlaskRedis(app, decode_responses=True)


@app.route('/')
def index():
    crawl_status = {
        '1': '待抓取',
        '2': '抓取中',
        '3': '抓取完成',
        '4': '抓取失败',
        'xiaoqu': '小区房价',
        'ershou': '挂牌二手房',
        'loupan': '新房',
    }
    results = get_db_city()
    crawl_tasks = list()

    crawl_task = redis_client.hgetall('crawl_task')
    for task in crawl_task:
        crawl_tasks.append((
            str(task).split('_')[0],
            str(task).split('_')[1],
            str(task).split('_')[2],
            str(crawl_task[task]),
        ))
    content = {
        "cities": results['result_city'],
        "result_fang": results['result_fang'],
        "result_ershou": results['result_ershou'],
        "crawl_status": crawl_status,
        "crawl_tasks": crawl_tasks,
    }
    return render_template('index.html', **content)


@app.route('/delete')
def delete():
    request_param = request.values.to_dict()
    redis_client.hdel('crawl_task', '_'.join((
            request_param['house_type'],
            request_param['city'],
            request_param['area'],
         )))
    return redirect(url_for('index'))


@app.route('/result')
def result():
    request_param = request.values.to_dict()
    results = get_info(request_param['house_type'], request_param['city'], request_param['area'])
    if results:
        try:
            content = {
                'results': results[:50],
                'request_param': request_param
            }
        except Exception as e:
            app.logger.error(e)
            content = {}
    else:
        content = {}
    return render_template('result.html', **content)


@app.route('/download')
def download_file():
    request_param = request.values.to_dict()
    results = get_info(request_param['house_type'], request_param['city'], request_param['area'])
    if results:
        date = get_date_string()
        csv_path = DATA_PATH + "/{}_{}_{}_{}.csv".format(date, request_param['house_type'], request_param['city'], request_param['area'])
        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(results)
    else:
        csv_path = None
    file_name = get_date_string() + "_{}_{}_{}.csv".format(request_param['house_type'], request_param['city'], request_param['area'])

    return send_file(csv_path, mimetype='text/csv', attachment_filename=file_name, as_attachment=True)


@app.route('/grab', methods=['POST'])
def grab():
    request_param = request.values.to_dict()
    if all(i in request_param for i in ('city', 'house_type', 'area', 'province')) and \
            all((request_param['city'], request_param['house_type'])):
        redis_client.hset('crawl_task', '_'.join((
            request_param['house_type'],
            request_param['city'],
            request_param['area'],
         )), 1)
        queues.put((
            request_param['house_type'],
            request_param['city'],
            request_param['area'],
        ))
        app.logger.info("已推到队列！！！ {}".format('_'.join((
            request_param['house_type'],
            request_param['city'],
            request_param['area'],
         ))))
    else:
        return json.dumps({'status': "0", "result": "parameter error!!!"})
    return json.dumps({'status': "1", "result": "Ready to grab!!!"})


@app.route('/get_city', methods=['GET'])
def get_city():
    result = get_area_city()
    if result:
        return json.dumps({'status': 1, "result": result})
    return json.dumps({'status': 0, "result": None})


@app.route('/get_xiaoqu_detail', methods=['GET'])
def get_xiaoqu_detail():
    request_param = request.values.to_dict()
    results = get_xiaou_detail(request_param['xiaoqu_name'])
    if results:
        try:
            content = {
                'results': results
            }
        except Exception as e:
            app.logger.error(e)
            content = {}
    else:
        content = {}

    return render_template('xiaoqu_detail.html', **content)


def run_spider(queues):
    app.logger.info('在循环队列')
    while True:
        try:
            data = queues.get(timeout=10)
        except Exception:
            app.logger.info('队列是空的')
            break
        redis_client.hset('crawl_task', '_'.join(data), 2)
        result = get_crawl_task(*data)
        if not result:
            try:
                crawl_time = 0
                if data[0] == 'xiaoqu':
                    crawl_time = XiaoQuBaseSpider(data[1], data[2]).start()
                elif data[0] == 'ershou':
                    crawl_time = ErShouSpider(data[1], data[2]).start()
                elif data[0] == 'loupan':
                    crawl_time = LouPanBaseSpider(data[1], data[2]).start()

                if crawl_time and insert_crawl_task(data[0], data[1], data[2], crawl_time):
                    app.logger.info("抓取完成!!!")
                    redis_client.hset('crawl_task', '_'.join(data), 3)
                else:
                    redis_client.hset('crawl_task', '_'.join(data), 4)
            except Exception as e:
                redis_client.hset('crawl_task', '_'.join(data), 4)
                app.logger.error(e)
        else:
            redis_client.hset('crawl_task', '_'.join(data), 3)
            app.logger.info("已经抓过。")


if __name__ == '__main__':
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    app.run(host=HOST, port=PORT, debug=DEBUG)
