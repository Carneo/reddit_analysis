from django.template import RequestContext,loader 
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic.base import View
from django.shortcuts import render, get_object_or_404
from models import *
from forms import SearchForm
from django.shortcuts import render_to_response
# from celery.result import AsyncResult
import simplejson

###### 
######
##### REMEMBER MOST OF YOUR STATIC STUFF IS FOR DEVELOPMENT ONLY. FIX 
class IndexView(View):
    template_name = 'reddit_analysis/index.html'
    form_class = SearchForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
        
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        username = request.POST.get('user')
        error_message = "User does not exist"
        r_user = self.user_found(username)
        # progress = r_user.result or r_user.state 

        if not r_user:
            return render(request, 'reddit_analysis/index.html', {'error': error_message })

        if self.user_in_db(username):
            user = User.objects.get(username=username)
            user.count += 1
            user.save() 
        else: 
            user = User(username=username, count=1)
            user.save()


        top_words = r_user.top_words(size='max')
        unique_words = r_user.get_unique_words()
        subreddits_filter = r_user.top_words_by_subreddits() # size == max
         
        from datetime import date 
        # Bug fix: adds subbreddits, but the post/comment may be out of bounds. 
        subreddits = [s for s in subreddits_filter.keys() if len(subreddits_filter[s]) > 0]
        sub_activity = r_user.subreddit_activity()
        yearly_activity = r_user.yearly_posting_activity()
        years = yearly_activity.keys()
        current_year = str(date.today().year)
        comment_count = r_user.comment_count()
        post_count = r_user.post_count()
        karma_p_p = r_user.avg_karma_p_post()

        get_b = r_user.get_best_comment()
        karma_best = get_b[0]
        best = get_b[1]
        get_w = r_user.get_worst_comment()
        karma_worst = get_w[0]
        worst = get_w[1]
       
        acc_created = r_user.account_created()
        karma = r_user.get_karma()
        comment_karma = r_user.get_comment_karma()
        submission_karma = r_user.get_submission_karma()
        karma_p = r_user.avg_karma_p_comment()
        word_count = r_user.get_word_count()
        stop_count = r_user.get_stop_count()
        comment_length = r_user.avg_comment_length()
        edited = r_user.percent_edited()
        sub_rec = r_user.subreddit_recommendation()
        lang = r_user.language_usage()
        post_types = r_user.post_types()
        # Deal with NoneType/Attribute errors. 
        if comment_count > 0:
            get_first = r_user.get_earliest_comment()
            date = get_first[0]
            first_comment = get_first[1]
        else:
            get_first = None
            date = None
            first_comment = None

        #### CHART SERIES' ##### 
        top_chart_series = self.top_words_series(top_words)
        sub_chart_series = self.pie_series('Activity share', sub_activity)
        post_types_series = self.pie_series('Type share', post_types,)
        lang_series = self.lang_series(lang)
        yearly_activity_series = self.yearly_series(yearly_activity)
        subreddits_series = self.subreddit_series(subreddits_filter)

        # try: 
        #     liked = r_user.liked_content()
        #     disliked = r_user.disliked_content() 
        # except Exception: # FIX 
        #     like_chart = None
        #     dis_chart = None
        # else: 
        #     like_chart = self.pie_view(liked, 'Upvoted content by subreddit')
        #     dis_chart = self.pie_view(disliked, 'Downvoted content by subreddit')

        return render(request, 'reddit_analysis/detail.html', {'user': user,
                    'top_chart_series': top_chart_series,
                    'sub_chart_series': sub_chart_series,
                    'comment_length': comment_length,
                    'unique_words': unique_words,
                    'lang_series': lang_series,
                    'edited': edited,
                    'word_count': word_count,
                    'stop_count': stop_count,
                    'comment_length': comment_length,
                    'comment_count': comment_count,
                    'post_count': post_count,
                    'best': best,
                    'first_comment': first_comment,
                    'karma': karma,
                    'comment_karma': comment_karma,
                    'submission_karma': submission_karma,
                    'karma_p': karma_p,
                    'karma_p_p': karma_p_p,
                    'karma_best': karma_best,
                    'date': date,
                    'years': years,
                    'yearly_activity_series': yearly_activity_series,
                    'sub_rec': sub_rec,
                    'karma_worst': karma_worst,
                    'worst': worst,
                    'post_types_series': post_types_series,
                    'subreddits': subreddits,
                    'acc_created': acc_created,
                    'subreddits_series': subreddits_series,
                    'current_year': current_year
                    })

    def user_in_db(self, user):
        return User.objects.filter(username=user).count() == 1 

    def user_found(self, user):
        try:
            user = ra.User_Analysis(user)
        except ra.praw.requests.exceptions.HTTPError:
            return False 
        else: 
            return user 

    ### PY TO JSON 
    def top_words_series(self, d):

       if len(d) > 0: 
            words, count = zip(*d)
       else: 
            words, count = ['None'], [0] 
 
       series = {
       'categories': self.dumps(words),
       'data': self.dumps([{'data': count, 'name': 'Word Occurence'}])}

       return series

    def subreddit_series(self, d):
        data = dict()

        for sub, v in d.items(): 
            try: 
                words, count = zip(*d[sub])
                data[sub] = [words, count]
            except Exception:
                pass


        series = {'data': self.dumps([{'data': data, 'name': 'Word Occurence'}])}

        print series 
        return series 

    def lang_series(self, data):
       d = [list((k, v)) for k,v in data.items() if k != 'swedish' and v > 5] 
       # quick fix for swedish language bug. Sorry Sweeds... If anyone knows how to do a better job with the language checker, feel free to pm me. 

       return {'data': self.dumps([{'name': 'Usage amongst comments', 'data': d}])}

    def pie_series(self, name, data):
       d = [list((k, v)) for k,v in data.items()]

       return {'data': self.dumps([{'name': name, 'data': d}])}

    def yearly_series(self, data):
        return {'data': self.dumps([{'name': 'Posts', 'data': data}])}
       
    def dumps(self, obj):
        return simplejson.dumps(obj)
        
class InfoView(View):
    template_name = 'reddit_analysis/info.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class StopListView(View):
    template_name = 'reddit_analysis/stop_list.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'english_list': ra.ENGLISH_STOPWORDS, 'rest': ra.STOPWORDS_DICT})
