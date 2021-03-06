import json
import pdb
import time
import datetime
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum, Count
from _project.models import User, UserConfig, Label, List, Promo, Count, UserIn, UserFirstIn


# 返回日期
def getDate(obj):
    return datetime.datetime.strftime(obj['start_date'], '%Y-%m-%d')
# Create your views here.
# 注册接口
'''
register
@param username 用户名
@param password 用户密码
'''
def register(request):
    if request.method == 'POST':
        # 需要对body解码之后通过json解析成dict
        data = json.loads(request.body.decode())
        username = data['username']
        password = data['password']
        if User.objects.filter(username=username):
            # 已存在该用户名
            err_code = '100'
            status = False
        else:
            # 创建新的用户
            User.objects.create(username=username, password=password)
            status = True
            err_code = 1
        response = {
            "status": status,
            "err_code": err_code
        }
        return JsonResponse(response)

# 登录接口
'''
login
@param username 用户名
@param password 用户密码
'''
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode())
        username = data['username']
        password = data['password']
        try:
            # 查询是否该用户名
            user = User.objects.filter(username=username)
            if len(user) == 0:
                # 用户不存在
                status = False
                err_code = '100'
            else:
                user = user[0]
                # 密码不一样
                if user.password != password:
                    status = False
                    err_code = '101'
                else:
                    # 存取session
                    request.session['user_id'] = user.id
                    user_in = UserFirstIn.objects.filter(user_id=user.id)
                    if len(user_in) == 0:
                        UserFirstIn.objects.create(user_id=user.id)
                    status = True
                    err_code = 1
        except Exception as e:
            print(e)
            status = False
            err_code = 100
        response = {
            "status": status,
            "err_code": err_code
        }
        return JsonResponse(response)

# 退出登陆
'''
logout
@param user_id 用户id
'''
def logout(request):
    try:
        # 删除用户session
        del request.session['user_id']
    except:
        pass
    response = {
        'status': True,
        'err_code': 1
    }
    return JsonResponse(response)

# 密码查询
'''
confirmPass
@param password 加密后密码
'''
def confirmPass(request):
    old_password = json.loads(request.body.decode())['password']
    # pdb.set_trace()
    user_id = request.session['user_id']
    try:
        user = User.objects.get(id=user_id)
        if user.password == old_password:
            status = True
            err_code = 1
        else:
            status = False
            err_code = 1
    except Exception as e:
        print(e)
        status = False
        err_code = 100
    response = {
        "status": status,
        "err_code": err_code
    }
    return JsonResponse(response)

# 修改密码
'''
updatePass
@param password 加密后密码
'''
def updatePass(request):
    new_password = json.loads(request.body.decode())['newpass']
    user_id = request.session['user_id']
    try:
        user = User.objects.get(id=user_id)
        user.password = new_password
        user.save()
        status = True
        err_code = 1
    except Exception as e:
        print(e)
        status = False
        err_code = 100
    response = {
        "status": status,
        "err_code": err_code
    }
    return JsonResponse(response)

# 增加配置
'''
addConfig
@param focus_mins 专注时间
@param relax_mins 休息时间
@param relax_long_mins 长时间休息
@param relax_long_count 长时间间隔
@param use_notification 允许系统通知
@param auto_focus 自动专注
@param auto_relax 自动休息
'''
def addConfig(request):
    ''' addConfig '''
    if request.method == 'POST':
        data = json.loads(request.body.decode())
        user_id = request.session['user_id']
        try:
            # 更新用户配置
            config = UserConfig.objects.get(user_id=user_id)
            for key in data:
                setattr(config, key, data[key])
            config.save()
            status = True
            err_code = 1
        except:
            status = False
            err_code = 100
        response = {
            'status': status,
            'err_code': err_code
        }
        return JsonResponse(response)


# 查询个人配置
'''
config
@param focus_mins 专注时间
@param relax_mins 休息时间
@param relax_long_mins 长时间休息
@param relax_long_count 长时间间隔
@param use_notification 允许系统通知
@param auto_focus 自动专注
@param auto_relax 自动休息
'''
def config(request):
    ''' config '''
    if request.method == 'POST':
        user_id = request.session['user_id']
        # pdb.set_trace()
        # 如果查不到用户的配置数据，则新建一个
        try:
            # pdb.set_trace()
            config = UserConfig.objects.get(user_id=user_id)
        except:
            # pdb.set_trace()
            config  = UserConfig.objects.create(user_id=user_id)
        status = True
        err_code = 1
        data = {
            'focus_mins': config.focus_mins,
            'relax_mins': config.relax_mins,
            'relax_long_mins': config.relax_long_mins,
            'relax_long_count': config.relax_long_count,
            'use_notification': config.use_notification,
            'auto_focus': config.auto_focus,
            'auto_relax': config.auto_relax
        }
        response = {
            "status": status,
            "data": data,
            "err_code": err_code
        }
        return JsonResponse(response)

# 获取所有标签的值
'''
getlabel
@param id label_id
@param name label_name
'''
def getLabel(request):
    ''' label '''
    label = []
    try:
        # pdb.set_trace()
        labels = Label.objects.all().values()
        for item in labels:
            obj = {
                'value': item['id'],
                'label': item['name']
            }
            label.append(obj)
        status = True
        err_code = 1
    except:
        status = False
        err_code = 100
    response = {
        'status': status,
        'label': label,
        'err_code': err_code
    }
    return JsonResponse(response)

'''
getList
@param user_id 用户id
@param lists 用户的任务清单
    @param list_id list_id
    @param title 名称
    @param label label_id
    @param start_time 预计开始时间
    @param summary 总结
    @param complete 完成标志
    @param tmt_counts 预计完成番茄数
    @param complete_counts 实际完成番茄数
'''
def getList(request):
    ''' getList '''
    if request.method == 'POST':
        user_id =request.session['user_id']
        today = datetime.date.today().strftime('%Y-%m-%d')
        lists = []
        haveTodayList = False
        try:
            # all_lists
            all_lists = List.objects.filter(user_id=user_id, complete=False)
            # today_lists 获取今天的数据
            order_lists = list(all_lists.filter(start_time=today))
            if len(order_lists) != 0:
                haveTodayList = True
            # 获取其他的数据
            other_lists = list(all_lists.exclude(start_time=today).order_by('-start_time'))
            order_lists.extend(other_lists)
            labels = Label.objects.all()
            for item in order_lists:
                label_index_id = item.label_id - 1
                obj = {
                    'list_id': item.list_id,
                    'title': item.title,
                    'label': labels[label_index_id].name,
                    'start_time': item.start_time,
                    'summary': item.summary,
                    'complete': item.complete,
                    'tmt_counts': item.tmt_counts,
                    'complete_counts': item.complete_counts
                }
                lists.append(obj)
            status = True
            err_code = 1
        except Exception as e:
            print(e)
            status = False
            err_code = 100
        response = {
            "status": status,
            "list": lists,
            "have_todaylists": haveTodayList,
            "err_code": err_code
        }
        return JsonResponse(response)

# 增加个人清单
'''
addlist
@param user_id 用户id
'''
def addList(request):
    if request.method == 'POST':
        list_info = json.loads(request.body.decode())
        user_id = request.session['user_id']
        try:
            new_list = List(user_id=user_id)
            for key in list_info:
                if key == 'label':
                    new_list.label_id = list_info[key]
                else :
                    setattr(new_list, key, list_info[key])
            new_list.save()
            status = True
            err_code = 1
        except:
            status = False
            err_code = 100
        response = {
            'status': status,
            'err_code': err_code
        }
        return JsonResponse(response)

# 删除个人清单
'''
:param list_id
'''
def delList(request):
    ''' delList '''
    if request.method == 'POST':
        data = json.loads(request.body.decode())
        list_id = data['list_id']
        user_id = request.session['user_id']
        try:
            # pdb.set_trace()
            del_list = List.objects.filter(list_id=list_id)[0]
            count_pros = Promo.objects.filter(promo_id=list_id)
            for pro in count_pros:
                day = pro.start_date.date()
                old_count = Count.objects.get(user_id=user_id, today_date=day)
                old_count.count_promos -= 1
                old_count.count_mins = old_count.count_mins - pro.pro_mins
                old_count.save()
            del_list.delete()
            count_pros.delete()
            # count_pro_mins = int(Promo.objects.filter(promo_id=list_id).aggregate(promo_count_mins=Sum('pro_mins'))['promo_count_mins'])
            # count = Count.objects.get(user_id=user_id)
            # count.count_mins 
            # .delete()
            status = True
            err_code = 1
        except Exception as e:
            print(e)
            status = False
            err_code = 100
        response = {
            'status': status,
            'err_code': err_code
        }
        return JsonResponse(response)

# 完成任务
'''
doneList
@param summary 总结
@param list_id list_id
@param complete 完成标志
@param done_time 完成时间 
'''
def doneList(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode())
        summary = data['summary']
        list_id = data['list_id']
        # pdb.set_trace()
        try:
            done_list = List.objects.get(list_id=list_id)
            # 保存总结
            done_list.summary = summary
            # 修改完成标志
            done_list.complete = True
            # 记录完成时间
            done_list.done_time = datetime.datetime.now()
            if done_list.end_date == None:
                all_promos = Promo.objects.filter(promo_id=list_id).order_by('-end_date')
                if len(all_promos) != 0:
                    done_list.end_date = all_promos[0].end_date
                else:
                    done_list.end_date = datetime.datetime.now()
            if done_list.start_date == None:
                done_list.start_date =  datetime.datetime.now()
            done_list.save()
            status = True
            err_code = 1
        except Exception as e:
            print(e)
            status = False
            err_code = 100
        response = {
            'status': status,
            'err_code': err_code
        }
        return JsonResponse(response)


# 查询个人清单
'''
listSearchDate
@param start_time 查询开始时间
@param end_time 查询结束时间
@prama label_id label_id
'''
def listSearchDate(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode())
        start_time = datetime.datetime.strptime(data['start_time'], '%Y-%m-%d')
        end_time = datetime.datetime.strptime(data['end_time'], '%Y-%m-%d')
        user_id = request.session['user_id']
        labels = Label.objects.all()
        lists = []
        try:
            filter_lists = List.objects.filter(user_id=user_id, start_time__range=(start_time, end_time)).order_by('-start_time')
            for item in filter_lists:
                label_index_id = item.label_id - 1
                obj = {
                    'list_id': item.list_id,
                    'title': item.title,
                    'label': labels[label_index_id].name,
                    'start_time': item.start_time,
                    'summary': item.summary,
                    'complete': item.complete,
                    'tmt_counts': item.tmt_counts,
                    'complete_counts': item.complete_counts
                }
                lists.append(obj)
            status = True
            err_code = 1
        except Exception as e:
            print(e)
            status = False
            err_code = 100
        response = {
            "status": status,
            'list': lists,
            "err_code": err_code
        }
        return JsonResponse(response)

'''
@param start_date 开始时间
@param end_date 结束时间 --建立的时候自动创建
@param promo promo_id
@param label label_id
@param user_id user_id
'''
# 增加番茄
def addPromo(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode())
        promo_id = data['list_id']
        user_id =request.session['user_id']
        start_date = data['start_date']
        label = data['label']
        promo_mins = data['promoMins']
        today_date = datetime.datetime.now().date()
        try:
            # 获取label_id
            label_id = Label.objects.get(name=label).id
            # 创建新的番茄
            new_promo = Promo(user_id=user_id, promo_id=promo_id)
            # 存取开始时间
            new_promo.start_date = datetime.datetime.fromtimestamp(start_date / 1000)
            new_promo.label_id = label_id
            new_promo.pro_mins = promo_mins
            up_list = List.objects.get(user_id=user_id, list_id=promo_id)
            up_list.complete_counts = up_list.complete_counts + 1
            # 添加第一次开始时间
            if up_list.start_date == None:
                up_list.start_date = datetime.datetime.fromtimestamp(start_date / 1000)
            # 添加统计
            new_count = Count.objects.filter(today_date=today_date, user_id=user_id)
            if len(new_count) == 0:
                new_count = Count(user_id=user_id)
            else:
                new_count = new_count[0]
            new_count.count_promos += 1
            new_count.save()
            new_promo.save()
            up_list.save()
            status = True
            err_code = 1
        except Exception as e:
            print(e)
            status = False
            err_code = 100
        response = {
            "status": status,
            "err_code": err_code 
        }
        return JsonResponse(response)

# 获取统计分钟数
'''
getCountMins
@param count_mins 完成分钟
'''
def getCountMins(request):
    if request.method == 'GET':
        user_id = request.session['user_id']
        today_date = datetime.datetime.now().date()
        count_mins = 0
        try:
            new_count = Count.objects.filter(today_date=today_date, user_id=user_id)
            if len(new_count) == 0:
                new_count = Count.objects.create(user_id=user_id)
            else:
                new_count = new_count[0]
            count_mins = new_count.count_mins
            status = True
            err_code = 1
        except Exception as e:
            print(e)
            status = False
            err_code = 100
        response = {
            "status": status,
            "count_mins": count_mins,
            "err_code": err_code
        }
        return JsonResponse(response)


# 添加统计分钟数
'''
addCountMins
'''
def addCountMins(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode())
        count_mins = data['countMins']
        user_id = request.session['user_id']
        today_date = datetime.datetime.now().today()
        try:
            up_count = Count.objects.get(user_id=user_id, today_date=today_date)
            up_count.count_mins = count_mins
            up_count.save()
            status = True
            err_code = 1
        except Exception as e:
            print(e)
            status = False
            err_code = 100
        response = {
            "status": status,
            "err_code": err_code
        }
        return JsonResponse(response)

# 查询番茄数据
'''
getPromo
@param user_id user_id
@param start_date 开始时间 '%Y-%m-%d'
@param end_date 结束时间 '%Y-%m-%d'
'''
def getPromo(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode())
        user_id = request.session['user_id']
        start_date = data['start_date']
        end_date = data['end_date']
        labels = Label.objects.all()
        dataList = []
        try:
            # pdb.set_trace()
            if start_date != '':
                start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
                end_date = datetime.datetime.combine(end_date, datetime.time.max)
                # search_promo = Promo.objects.filter(user_id=user_id).order_by('-start_date')
                search_promo = Promo.objects.filter(user_id=user_id, start_date__range=(start_date, end_date)).order_by('-start_date')
            else:
                search_promo = Promo.objects.filter(user_id=user_id).order_by('-start_date')
            dates = list(set(map(getDate, search_promo.values('start_date'))))
            for date in dates:
                obj = {}
                promoList = []
                obj['date'] = date
                fdate = datetime.datetime.strptime(date, '%Y-%m-%d')
                end_fdate = datetime.datetime.combine(fdate, datetime.time.max)
                insert_promo = search_promo.filter(start_date__range=(fdate, end_fdate))
                for item in insert_promo:
                    promo_id = item.promo_id
                    label_id = item.label_id
                    s_date = item.start_date.strftime('%H:%M')
                    e_date = item.end_date.strftime('%H:%M')
                    insert_list = List.objects.get(list_id=promo_id)
                    title = insert_list.title
                    label = labels[label_id-1].name
                    summary = insert_list.summary
                    pobj = {
                        "id": item.id,
                        "list_id": promo_id,
                        "title": title,
                        "label": label,
                        "start_date": s_date,
                        "end_date": e_date,
                        "summary": summary
                    }
                    promoList.append(pobj)
                obj['promoList'] = promoList
                dataList.append(obj)
            status = True
            err_code = 1
        except Exception as e:
            print(e)
            status = False
            err_code = 100
        response = {
            "status": status,
            "data": dataList,
            "err_code": err_code
        }
        return JsonResponse(response)


# 删除番茄数据
'''
delPromo
@param user_id user_id
@param list_id list_id
@param day 今天日期
@param start_date 开始时间 %H:%M:%S
@param end_date 结束时间 %H:%M:%S
'''
def delPromo(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode())
        user_id = request.session['user_id']
        # list_id = data['list_id']
        day = data['day']
        promo_id = data['id']
        # start_date = datetime.datetime.strptime(day + ' ' + data['start_date'], '%Y-%m-%d %H:%M')
        # end_date = datetime.datetime.strptime(day + ' ' + data['end_date'], '%Y-%m-%d %H:%M')
        day_date = datetime.datetime.strptime(day, '%Y-%m-%d')
        try:
            # pdb.set_trace()
            # Promo.objects.filter(user_id=user_id, promo_id=list_id, start_date=start_date, end_date=end_date).delete()
            del_promo = Promo.objects.filter(id=promo_id)
            # del_promo = Promo.objects.filter(user_id=user_id, promo_id=list_id, start_date__date=start_date.date(), start_date__hour=start_date.hour, start_date__minute=start_date.minute, end_date__hour=end_date.hour, end_date__minute=end_date.minute)
            promo_mins = del_promo[0].pro_mins
            old_count = Count.objects.get(user_id=user_id, today_date=day_date)
            old_count.count_promos = old_count.count_promos - 1
            old_count.count_mins = old_count.count_mins - promo_mins
            old_count.save()
            del_promo.delete()
            status = True
            err_code = 1
        except Exception as e:
            print(e)
            status = False
            err_code = 100
        response = {
            "status": status,
            "err_code": err_code
        }
        return JsonResponse(response)

# 查询完成清单数据
'''
getCompleteList
@param user_id user_id
@param start_date 搜索开始时间 %Y-%m-%d
@param end_date 搜索开始时间 %Y-%m-%d
'''
def getCompleteList(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode())
        user_id = request.session['user_id']
        start_date = data['start_date']
        end_date = data['end_date']
        lists = []
        try:
            # pdb.set_trace()
            if start_date != '':
                start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
                # 当天最后时间
                end_date = datetime.datetime.combine(end_date, datetime.time.max)
                all_lists = List.objects.filter(user_id=user_id, complete=True, done_time__range=(start_date, end_date)).order_by('-done_time')
            else:
                # all_lists
                all_lists = List.objects.filter(user_id=user_id, complete=True).order_by('-done_time')
            labels = Label.objects.all()
            for item in all_lists:
                list_id = item.list_id
                label_index_id = item.label_id - 1
                # promoLists = Promo.objects.filter(promo_id=list_id, user_id=user_id)
                # 获取第一次开始时间
                start_time = item.start_date
                # 获取最后一次结束时间
                end_time = item.end_date
                real_days = (end_time - start_time).days
                plane_start_time = item.start_time
                plane_end_time = item.end_time
                plan_days = (plane_end_time - plane_start_time).days
                obj = {
                    'list_id': list_id,
                    'title': item.title,
                    'label': labels[label_index_id].name,
                    'start_time': start_time.strftime('%Y-%m-%d'),
                    'end_time': end_time.strftime('%Y-%m-%d'),
                    'real_days': real_days + 1,
                    'plane_start_time': plane_start_time.strftime('%Y-%m-%d'),
                    'plane_end_time': plane_end_time.strftime('%Y-%m-%d'),
                    'plan_days': plan_days + 1,
                    'summary': item.summary,
                    'complete': item.complete,
                    'tmt_counts': item.tmt_counts,
                    'complete_counts': item.complete_counts
                }
                lists.append(obj)
            status = True
            err_code = 1
        except Exception as e:
            print(e)
            status = False
            err_code = 100
        response = {
            "status": status,
            "data": lists,
            "err_code": err_code
        }
        return JsonResponse(response)

# 修改完成清单数据
'''
updateCompleteList
@param user_id user_id
@param list_id list_id
@param summary 总结
'''
def updateCompleteList(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode())
        user_id = request.session['user_id']
        list_id = data['list_id']
        try:
            up_list = List.objects.get(user_id=user_id, list_id=list_id)
            up_list.summary = data['summary']
            up_list.save()
            status = True
            err_code = 1
        except Exception as e:
            print(e)
            status = False
            err_code = 100
        response = {
            "status": status,
            "err_code": err_code
        }
        return JsonResponse(response)


# 删除完成清单数据
'''
delCompleteList
@param list_id list_id
'''
def delCompleteList(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode())
        user_id = request.session['user_id']
        list_id = data['list_id']
        try:
            up_list = List.objects.get(user_id=user_id, list_id=list_id)
            up_list.complete = False
            up_list.save()
            status = True
            err_code = 1
        except Exception as e:
            print(e)
            status = False
            err_code = 100
        response = {
            "status": status,
            "err_code": err_code 
        }
        return JsonResponse(response)

# 获取初始统计数据
'''
getCountData
@return historyCountMins 至今为止的所有分钟数
@return historyCountPromos 至今为止的所有番茄数
@return historyCountList 至今为止的所有完成清单数
'''
def getCountData(request):
    user_id = request.session['user_id']
    data = {}
    try:
        # 至今为止的所有分钟数
        historyCountMins = int(Count.objects.filter(user_id=user_id).aggregate(history_count_mins=Sum('count_mins'))['history_count_mins'])
        # 至今为止的所有番茄数
        historyCountPromos = int(Count.objects.filter(user_id=user_id).aggregate(history_count_promos=Sum('count_promos'))['history_count_promos'])
        # 至今为止的所有完成清单数
        historyCountList = List.objects.filter(user_id=user_id,complete=True).count()
        status = True
        data = {
            "historyCountMins": historyCountMins,
            "historyCountPromos": historyCountPromos,
            "historyCountList": historyCountList
        }
        err_code = 1
    except Exception as e:
        print(e)
        status = False
        err_code = 100
    response = {
        "status": status,
        "data": data,
        "err_code": err_code
    }
    return JsonResponse(response)


# 获取不同日期下的番茄数
'''
getLineChart
@param start_date 开始时间
@param end_date 结束时间
'''
def getLineChart(request):
    def getDay(obj):
        return datetime.datetime.strftime(obj['today_date'], '%m-%d')
    def getPromos(obj):
        return obj['count_promos']
    if request.method == 'POST':
        data = json.loads(request.body.decode())
        user_id = request.session['user_id']
        start_date = data['start_date']
        end_date = data['end_date']
        today_date = datetime.datetime.now().date()
        seven_days_before = today_date - datetime.timedelta(days=7)
        chartData = {}
        try:
            if start_date != '':
                # pdb.set_trace()
                start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
                end_date = datetime.datetime.combine(end_date, datetime.time.max)
                days = (end_date - start_date).days
                date_list = [(start_date + datetime.timedelta(i)).strftime('%y-%m-%d') for i in range(days+1)]
                # date_lists
                # 搜索时间内的统计数据
                count_promos = Count.objects.filter(user_id=user_id, today_date__range=(start_date, end_date)).order_by('today_date')
            else:
                date_list = [(seven_days_before + datetime.timedelta(i+1)).strftime('%y-%m-%d') for i in range(7)]
                today_date = datetime.datetime.combine(today_date, datetime.time.max)
                count_promos = Count.objects.filter(user_id=user_id, today_date__range=(seven_days_before, today_date)).order_by('today_date')
            count_promo_date = count_promos.values('today_date', 'count_promos')
            promo_list = [0 for i in range(len(date_list))]
            for x in count_promo_date:
                d = datetime.datetime.strftime(x['today_date'], '%y-%m-%d')
                if d in date_list:
                    index = date_list.index(d)
                    promo_list[index] = x['count_promos']
            # dates = list(map(getDay, count_promos.values('today_date')))
            # promos = list(map(getPromos, count_promos.values('count_promos')))
            all_mins = count_promos.aggregate(all_mins=Sum('count_mins'))['all_mins']
            if not all_mins:
                all_mins = 0
            chartData = {
                "xdata": date_list,
                "ydata": promo_list,
                "allMins": all_mins
            }
            status = True
            err_code = 1
        except Exception as e:
            print(e)
            status = False
            err_code = 100
        response = {
            "status": status,
            "data": chartData,
            "err_code": err_code 
        }
        return JsonResponse(response)
        

# 获取标签分类
'''
getPieChart
'''
def getPieChart(request):
    def getLabelId(obj):
        return obj['label_id']
    if request.method == 'POST':
        user_id = request.session['user_id']
        chartData = {}
        labelData = []
        legend = []
        try:
            # pdb.set_trace()
            all_promo = Promo.objects.filter(user_id=user_id)
            labels_id = list(set(map(getLabelId, all_promo.values('label_id'))))
            label = Label.objects.all()
            for label_id in labels_id:
                label_name = label[label_id - 1].name
                label_count = all_promo.filter(label_id=label_id).count()
                obj = {
                    "value": label_count,
                    "name": label_name
                }
                labelData.append(obj)
                legend.append(label_name)
            chartData = {
                "legend": legend,
                "data": labelData
            }
            status = True
            err_code = 1
        except Exception as e:
            print(e)
            status = False
            err_code = 100
        response = {
            "status": status,
            "data": chartData,
            "err_code": err_code
        }
        return JsonResponse(response)



# 获取最佳工作时间最佳工作日
'''
getBarChart
'''
def getBarChart(request):
    if request.method == 'POST':
        weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        user_id = request.session['user_id']
        minsdata = [0 for x in range(7)]
        datesdata = [0 for x in range(24)]
        chartData = {}
        try:
            # 统计工作日时间 获取最佳工作日
            all_counts = Count.objects.filter(user_id=user_id).values('today_date','count_mins')
            for count in all_counts:
                index = count['today_date'].weekday()
                minsdata[index] += count['count_mins']
            # 找到最大数
            max_promo = max(minsdata)
            wdays = []
            if max_promo > 0:
                howmany_day = minsdata.count(max)
                # 当只有一个最大数
                if howmany_day == 1:
                    wdays.append(weekdays[minsdata.index(max_promo)])
                else:
                # 不止一个最大数
                    where = [i for i in range(7) if minsdata[i] == max_promo]
                    for i in where:
                        wdays.append(weekdays[i])
            # pdb.set_trace()
            # 获取最佳工作时间段
            all_promos = Promo.objects.filter(user_id=user_id)
            for promo in all_promos:
                # print(promo.start_date.hour)
                # 获取每个promo开始时间，并在该时间段所花番茄数上加1
                # hour_index = promo.start_date.hour + 1
                hour_index = promo.start_date.hour - 1
                datesdata[hour_index] += 1
            # 获取其中花费最多的时间段
            max_date = max(datesdata)
            bestdate = []
            if max_date > 0:
                # 计算是否只有一个最大数
                howmany_date = datesdata.count(max_date)
                if howmany_date == 1:
                    index_date = datesdata.index(max_date) + 1
                    if index_date == 24:
                        index_date = 0 
                    bestdate.append(index_date)
                    #  = str(index_date) + ':00-' + str(index_date + 1) + ":00"
                else:
                    where_date = [i for i in range(24) if datesdata[i] == max_date]
                    bestdate = []
                    for i in where_date:
                        index_date = i + 1
                        if index_date == 24:
                            index_date = 0
                        bestdate.append(index_date)
                        #  += str(index_date) + ':00-' + str(index_date + 1) + ":00"
                        # if i != len(where_date)-1:
                            # bestdate += ','
            chartData = {
                "xdata": weekdays,
                'ydata': minsdata,
                'bestdate': bestdate,
                'bestday': wdays
            }
            status = True
            err_code = 1
        except Exception as e:
            print(e)
            status = False
            err_code = 100
        response = {
            "status": status,
            "data": chartData,
            "err_code": err_code
        }
        return JsonResponse(response)


# 获取用户历史状态
def getUserStatus(request):
    def getLabelId(obj):
        return obj['label_id']
    if request.method == 'POST':
        user_id = request.session['user_id']
        today_date = datetime.datetime.now().date()
        last_day = today_date - datetime.timedelta(days=1)
        data = {}
        is_first_in = True
        is_show = False
        count_promo = 0
        count_complete_list = 0
        count_mins = 0
        count_label = []
        promo_list = []
        last_date = datetime.datetime.strftime(last_day, '%Y-%m-%d')
        # 如果获取得到今日用户进来数据，则isShow置为False，反之为True
        # pdb.set_trace()
        try:
            first_user = UserFirstIn.objects.get(user_id=user_id)
            is_first_in = first_user.is_first_in
            if is_first_in:
                first_user.is_first_in = False
                first_user.save()
            else:
                user = UserIn.objects.filter(user_id=user_id, today_date=today_date)
                if len(user) == 0:
                    user = UserIn.objects.create(user_id=user_id)
                    is_show = True
                else:
                    user = user[0]
                    is_show = False
                counts = Count.objects.filter(today_date=last_day, user_id=user_id)
                labels = Label.objects.all()
                if len(counts) != 0:
                    count_data = counts[0]
                    # 获取昨日番茄累计数
                    count_promo = count_data.count_promos
                    # 获取昨日累计分钟数
                    count_mins = count_data.count_mins
                # 获取昨日的番茄
                promos = Promo.objects.filter(start_date__date=last_day, user_id=user_id)
                # 获取昨日的标签统计
                labels_id = list(set(map(getLabelId, promos.values('label_id'))))
                for label_id in labels_id:
                    label_name = labels[label_id - 1].name
                    label_count = promos.filter(label_id=label_id).count()
                    obj = {
                        "value": label_count,
                        "name": label_name
                    }
                    count_label.append(obj)
                # 获取昨日的番茄详情
                for promo in promos:
                    obj = {
                        'start_time': datetime.datetime.strftime(promo.start_date, '%H:%M'),
                        'end_time': datetime.datetime.strftime(promo.end_date, '%H:%M'),
                        'title': List.objects.get(list_id=promo.promo_id).title
                    }
                    promo_list.append(obj)
                # 获取昨日完成的目标
                count_complete_list = List.objects.filter(user_id=user_id, done_time__date=last_day, complete=True).count()
            status = True
            err_code = 1
        except Exception as e:
            print(e)
            status = False
            err_code = 100
        data = {
            'date': last_date,
            'count_promo': count_promo,
            'count_list': count_complete_list,
            'count_mins': count_mins,
            'count_label': count_label,
            'promo_list': promo_list
        }
        response = {
            'status': status,
            'is_first_in': is_first_in,
            'is_show': is_show,
            'data': data,
            'err_code': err_code 
        }
        return JsonResponse(response)