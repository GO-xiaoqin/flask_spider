# Python爬虫程序
一个关于Flask、Python的页面封装程序，这个抓取程序的轮子不是我本人所写，抓取程序基础轮子是我在Github找的大佬的的程序改的原抓取程序的地址<https://github.com/jumper2014/lianjia-beike-spider>。  

环境配置：  
* Linux(CentOS 8.0)
* Python 3.6
* Docker
* MySQL 8.0
* Redis

配置说明：Python环境的包在 requirements.txt 有一个 DBUtils 的包没有更新，使用的时候可以单独install，这里用的Docker是因为我的MySQL以及Redis都是在Docker上跑的，如果你们用的是本机的数据库，则可以不用Docker，配置文件conf.py里面，配置简单即启即用，有能力的朋友可以修改一下server.sh文件启动程序，如果不太懂那就直接命令行python app.py 启动即可，文件夹下的uwsgi.ini文件是因为最初想用uwsgi对Flask包装一下的后来为了让程序不是那么复杂就算了。  

提示：在跑程序之前先建表（建表的SQL在sql_script文件夹下面），运行文件夹下的 get_*.py 三个文件把基础城市数据储存下来，在进行具体的启动抓取。

下面说一下程序：  
　　项目的启动文件 app.py 文件，启动成功通过浏览器操作程序对贝壳网的房产数据进行抓取，选择抓取类型、城市、区域，程序收到前端传来的参数等待入队列进行抓取，抓取过程实时更新Redis，同时MySQL也会进行重复过滤，单独维护一张 crawl_task 表判断一天内是否有创建任务，如果有则直接返回，抓取完成进行结果返回页面只返回查询结果的前五十条数据，如需看全部数据就要下载数据，程序会把结果存储到文件夹下./src/data/文件夹下面，返回前端数据流下载文件，由于是在大佬程序的基础上改的，还有一些功能没有完善，没用到的代码依然保留，以备后期添加新的功能。

最后，如果程序有问题，或贝壳网页面有变化，请留言，欢迎大家一起留言讨论，我们一起进步。


