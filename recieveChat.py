from bottle import request, route, run, template

import json


@route('/')
def index():
    # index.htmlの表示
    return template('index')


@route('/ajax_test')
def ajax_test():
    # クエリの取得
    queryDate = request.query.date

    # レスポンスの作成
    resDict = {
        'name': 'tamago',
        'age': '20',
        'date': queryDate
    }

    # JSON形式に変換し、返す
    return json.dumps(resDict)


run(host='localhost', port=3000, debug=True)