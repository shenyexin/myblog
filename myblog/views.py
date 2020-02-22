from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from read_count.utils import get_history_seven_days_read_data
from read_count.utils import get_today_data
from read_count.utils import get_yesterday_data
from read_count.utils import get_history_seven_day_data
from read_count.utils import get_history_thirty_day_data
from blog.models import Blog
from django.core.cache import cache

def home(request):
    context = {}
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates, read_nums = get_history_seven_days_read_data(blog_content_type)
    today_hot_data = get_today_data(blog_content_type)
    yesterday_hot_data = get_yesterday_data(blog_content_type)
    # history_seven_day_hot_data = get_history_seven_day_data(blog_content_type)
    history_thirty_day_hot_data = get_history_thirty_day_data(blog_content_type)

    # 获取7天热门博客的缓存数据
    cache_history_seven_day_hot_data = cache.get('cache_history_seven_day_hot_data')
    if cache_history_seven_day_hot_data is None:
        cache_history_seven_day_hot_data = get_history_seven_day_data(blog_content_type)
        print(cache_history_seven_day_hot_data)
        cache.set('cache_history_seven_day_hot_data', cache_history_seven_day_hot_data, 3600)
        print('setting')
    else:
        print('use cache')

    context['dates'] = dates
    context['read_nums'] = read_nums
    context['today_hot_data'] = today_hot_data
    context['yesterday_hot_data'] = yesterday_hot_data
    # context['history_seven_day_hot_data'] = history_seven_day_hot_data
    context['history_seven_day_hot_data'] = cache_history_seven_day_hot_data
    context['history_thirty_day_hot_data'] = history_thirty_day_hot_data
    return render(request, 'home.html', context)
