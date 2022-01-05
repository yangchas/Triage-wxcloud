import json
import logging
import os
import pickle

import jieba
import numpy as np
import pandas as pd
from django.http import JsonResponse
from django.shortcuts import render
from sklearn.feature_extraction.text import TfidfTransformer

from wxcloudrun.models import Counters
import joblib
from scipy.sparse import coo_matrix

logger = logging.getLogger('log')


def index(request, _):
    """
    获取主页

     `` request `` 请求对象
    """

    return render(request, 'index.html')


def counter(request, _):
    """
    获取当前计数

     `` request `` 请求对象
    """

    rsp = JsonResponse({'code': 0, 'errorMsg': ''}, json_dumps_params={'ensure_ascii': False})
    if request.method == 'GET' or request.method == 'get':
        rsp = get_count()
    elif request.method == 'POST' or request.method == 'post':
        rsp = update_count(request)
    else:
        rsp = JsonResponse({'code': -1, 'errorMsg': '请求方式错误'},
                            json_dumps_params={'ensure_ascii': False})
    logger.info('response result: {}'.format(rsp.content.decode('utf-8')))
    return rsp


def get_count():
    """
    获取当前计数
    """

    try:
        data = str(1)
    except Counters.DoesNotExist:
        return JsonResponse({'code': 0, 'data': 0},
                    json_dumps_params={'ensure_ascii': False})
    return JsonResponse({'code': 0, 'data': data},
                        json_dumps_params={'ensure_ascii': False})
#中文分词函数
def txt_cut(juzi):
    # 添加自定义词典和停用词典
    runpyp = os.path.abspath(__file__)
    modeldirp = os.path.dirname(runpyp)
    # modeldirp = '../'
    user_path = os.path.join(modeldirp, "dic/user_dict.txt")
    filter_path = os.path.join(modeldirp, "dic/filter.txt")
    jieba.load_userdict(user_path)
    stop_list = pd.read_csv(filter_path,
                            engine='python',
                            encoding='utf-8',
                            delimiter="\n",
                            names=['t'])['t'].tolist()
    return [w for w in jieba.lcut(juzi) if w not in stop_list]
def undir(s):
    return {1:'儿科',2:'内科',3:'五官科',4:'外科',5:'康复理疗科',6:'妇幼保健科',7:'妇产科',8:'口腔科',9:'精神科',10:'中医科',0:'皮肤科'}[s]
def update_count(request):
    """
    更新计数，自增或者清零

    `` request `` 请求对象
    """
    try:
        logger.info('update_count req: {}'.format(request.body))

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        age=body["age"]
        content=body["content"]
        sex=body["sex"]
        runpyp = os.path.abspath(__file__)
        modeldirp = os.path.dirname(runpyp)
        # modeldirp = '../'
        feature_path = os.path.join(modeldirp, "model/feature.pkl")
        vectorizer_model = pickle.load(open(feature_path, "rb"))
        model_path = os.path.join(modeldirp, "model/clf.model")
        clf_model = joblib.load(model_path)
        transformer = TfidfTransformer()
        content_cut=str(' '.join(txt_cut(content)))
        self_tf = vectorizer_model.transform([content_cut])
        pre = coo_matrix(self_tf, dtype=np.float32).toarray()
        age = int(age)
        pre = np.insert(pre, pre.shape[1], age, axis=1)
        sex = int(sex)
        pre = np.insert(pre, pre.shape[1], sex, axis=1)
        pre_y=clf_model.predict(pre)[0]
        pre_lable=undir(pre_y)
        return JsonResponse({'code': 1, "data": pre_lable,"msg":"预测成功"},
                        json_dumps_params={'ensure_ascii': False})
    except Exception:
        return JsonResponse({'code': 0, "data":"","msg": "啊哦发生错误了，请反馈给我们吧~"},
                        json_dumps_params={'ensure_ascii': False})