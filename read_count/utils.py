import datetime
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from .models import ReadNum, ReadDetail


def add_once_read_count(request, obj):
    ct = ContentType.objects.get_for_model(obj)
    key = "%s_%s_read" % (ct.model, obj.pk)
    if not request.COOKIES.get(key):
        # 阅读数+1
        # if ReadNum.objects.filter(content_type=ct, object_id=obj.pk).count():
        #     # 存在记录
        #     read = ReadNum.objects.get(content_type=ct, object_id=obj.pk)
        # else:
        #     read = ReadNum(content_type=ct, object_id=obj.pk)
        read, is_created = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk)
        read.read_num += 1
        read.save()

        # 当天阅读数+1
        date = timezone.now().date()
        read_detail, is_created = ReadDetail.objects.get_or_create(content_type=ct, object_id=obj.pk, date=date)
        read_detail.read_num += 1
        read_detail.save()
    return key


def get_history_seven_days_read_data(content_type):
    today = timezone.now().date()
    dates = []
    read_nums = []
    for i in range(6, -1, -1):
        date = today - datetime.timedelta(days=i)
        dates.append(date.strftime('%m/%d'))
        read_details = ReadDetail.objects.filter(content_type=content_type, date=date)
        result = read_details.aggregate(read_num_sum=Sum('read_num'))
        read_nums.append(result['read_num_sum'] or 0)
    return dates, read_nums


def get_today_data(content_type):
    today = timezone.now().date()
    read_details = ReadDetail.objects.filter(content_type=content_type, date=today).order_by('-read_num')
    return read_details[:5]  # limit


def get_yesterday_data(content_type):
    today = timezone.now().date()
    yesterday = today - datetime.timedelta(days=1)
    read_details = ReadDetail.objects.filter(content_type=content_type, date=yesterday).order_by('-read_num')
    return read_details[:5]


def get_history_seven_day_data(content_type):
    today = timezone.now().date()
    start_day = today - datetime.timedelta(days=7)
    read_details = ReadDetail.objects.filter(
        content_type=content_type, date__lte=today, date__gt=start_day
    ).annotate(read_num_sum=Sum('read_num')).order_by('-read_num')
    return read_details[:5]


def get_history_thirty_day_data(content_type):
    today = timezone.now().date()
    start_day = today - datetime.timedelta(days=30)
    read_details = ReadDetail.objects.filter(
        content_type=content_type, date__lte=today, date__gt=start_day
    ).annotate(read_num_sum=Sum('read_num')).order_by('-read_num')
    return read_details[:5]
