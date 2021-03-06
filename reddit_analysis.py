import datetime, os, collections
import praw, urllib2
import nltk
# from celery import task, current_task
# from celery.utils.log import get_task_logger

r = praw.Reddit('RedditAnalyser, written by /u/vicstudent')

punc = ". , ! ? ' ; :".split()
 

nltk.data.path.append('/home/carneos/webapps/reddit_analysis/redditAnalysis/reddit_analysis/nltk_data/')
ENGLISH_STOPWORDS = set(['all', 'think', 'consider', 'just', 'being', 'over', 'four', 'through', 'contains', 'yourselves', 'go', 'its', 'fifth', 'before', 'certainly', 'now', 'group', 'woman', 'with', 'had', 'should', 'to', 'only', 'under', 'ours', 'has', 'might', 'do', 'them', 'his', 'around', 'get', 'very', 'cannot', 'know', 'they', 'despite', 'not', 'during', 'yourself', 'him', 'nor', 'like', 'gets', 'd', 'did', 'p', 'good', 't', 'each', 'become', 'where', 'because', 'people', 'doing', 'theirs', 'some', 'up', 'are', 'year', 'cant', 'our', 'ourselves', 'out', 'what', 'for', 'shall', 'below', 'does', 'above', 'between', 'she', 'be', 'we', 'after', 'given', 'here', 'didnt', 'hers', 'eye', 'come', 'by', 'on', 'about', 'her', 'world', 'getting', 'of', 'k', 'allows', 'against', 'thing', 's', 'must', 'place', 'changes', 'or', 'comes', 'first', 'own', 'dont', 'feel', 'into', 'number', 'one', 'down', 'alone', 'appropriate', 'couldnt', 'your', 'considering', 'use', 'from', 'would', 'their', 'there', 'been', 'few', 'accordingly', 'much', 'too', 'way', 'themselves', 'was', 'until', 'more', 'himself', 'lot', 'both', 'company', 'c', 'but', 'off', 'believe', 'herself', 'than', 'those', 'he', 'me', 'also', 'myself', 'this', 'work', 'whom', 'will', 'while', 'can', 'were', 'problem', 'gives', 'my', 'could', 'say', 'theres', 'and', 'ive', 'have', 'then', 'is', 'in', 'am', 'it', 'an', 'as', 'itself', 'im', 'at', 'want', 'further', 'id', 'if', 'these', 'no', 'make', 'that', 'when', 'same', 'any', 'how', 'other', 'which', 'you', 'really', 'week', 'again', 'may', 'who', 'most', 'amongst', 'such', 'why', 'man', 'a', 'don', 'described', 'i', 'youre', 'anybody', 'having', 'person', 'definitely', 'so', 'time', 'the', 'thats', 'yours', 'fact', 'once'])
    
NON_ENGLISH_STOPWORDS = set(nltk.corpus.stopwords.words()) - ENGLISH_STOPWORDS
 
STOPWORDS_DICT = {lang: set(nltk.corpus.stopwords.words(lang)) for lang in nltk.corpus.stopwords.fileids()}
STOPWORDS_DICT['english'] = ENGLISH_STOPWORDS

def get_language(text):
    words = set(nltk.wordpunct_tokenize(text.lower()))
    return max(((lang, len(words & stopwords)) for lang, stopwords in STOPWORDS_DICT.items()), key = lambda x: x[1])[0]
    
      
class R_User(object):
    """ Reddit user object, initialized with basic data. """
    
    # @task()
    def __init__(self, user_name, comment=None):
        self.user = r.get_redditor(user_name)
        self.username = self.user.name
        
        # Important stuff 
        self.posts = dict() # {count: post}  
        self.comments = dict() # {count: comment}

        # Word data
        self.word_count = [0,0] # 0=total; 1=words that were checked off. 
        self.unique_words = 0

        # Comments 
        self.best_comment = [0, None] # score, comment 
        self.worst_comment = [0, None]
        self.comment_karma = self.user.comment_karma 

        # Submissions 
        self.best_post = [0, None]
        self.worst_post = [0, None]
        self.submission_karma = self.user.link_karma 

        # Other 
        self.karma = self.submission_karma + self.comment_karma
        self.sub_activity = dict()    
        self.lang_usage = {'portuguese': 0,
                               'english': 0, 
                               'swedish': 0,
                               'hungarian': 0,
                               'finnish': 0,
                               'danish': 0, 
                               'german': 0,
                               'spanish': 0,  
                               'french': 0, 
                               'norwegian': 0,
                               'dutch': 0, 
                               'russian': 0,
                               'turkish': 0, 
                               'italian': 0}
        
        def _best_worst(best, worst, score, data):
            """ Best and worst are either a comment or post, but must be the same unless you want bad data.
            """ 
            if score < worst[0]:
                worst[0], worst[1] = score, data 
            if score > best[0]:
                best[0], best[1] = score, data 
        # Store comments so it's quicker to access.
        c_count = 0
        for c in self.user.get_comments(self, limit=None):
            c_count += 1
            # First comment is default. 
            if c_count == 1: 
                self.worst_comment = [c, c.score] 
            _best_worst(self.best_comment, 
                        self.worst_comment,
                        c.score,
                        c) 
        
            body = c.body
            lang = get_language(body)
            self.lang_usage[lang] += 1
            self.word_count[0] += len(body)
            self.comments[c_count] = c


        # Best and worst posts 
        s_count = 0
        for s in self.user.get_submitted(self, limit=None):
            s_count += 1
            if s_count == 1: 
                self.worst_post = [s, s.score]

            _best_worst(self.best_post, 
                        self.worst_post, 
                        s.score,
                        s)
            self.posts[s_count] = s


            
    def __str__(self):
        return "User: %s" % self.username
        
    def get_user(self):
        return self.user
    
    def get_karma(self):
        return self.karma 
    
    def get_comment_karma(self):
        return self.comment_karma
    
    def get_submission_karma(self):
        return self.submission_karma

    def get_created(self):
        return self.user.created_utc
   
    def get_comments(self, subreddit_filter=[]):
        if subreddit_filter:
            return (c for c in self.comments.values()
                    if c.subreddit.display_name == subreddit_filter)
        else:     
            return self.comments.values()
        
    def get_posts(self, subreddit_filter=None):
        if subreddit_filter:
            return (p for p in self.posts
                    if p.subreddit.display_name == subreddit_filter)        
        else:
            return self.posts.values()
    
    def comment_count(self):
        return len(self.comments)

    def post_count(self):
        return len(self.posts)
    
    def get_word_count(self):
        return self.word_count[0]

    def get_unique_words(self):
        return self.unique_words
    
    def get_subreddits(self):
        return self.get_subreddit_activity().keys()
        
    def get_subreddit_activity(self):
        self.add_to_sub(self.get_posts())
        self.add_to_sub(self.get_comments())
        return self.sub_activity
    
    def get_subreddits(self):
        return self.get_subreddit_activity().keys()    
    
    def get_stop_count(self):
        return self.word_count[1]
    
    # Liked and disliked need authentication. 
    def get_liked_content(self):
        return self.user.get_disliked()
    
    def get_disliked_content(self):
        return self.user.get_liked()
    
    def add_to_stop_count(self):
        self.word_count[1] +=1 
        
    def add_to_sub(self, items):
        for i in items:
            self.add_subreddit(i)
                
    def add_subreddit(self, content):
        name = content.subreddit.display_name 
        if name in self.sub_activity:
            self.sub_activity[name] += 1
        else: 
            self.sub_activity[name] = 1      
   
class User_Analysis(R_User):
    """ Analysis class which supports the following methods:
        
        top_words
        subreddit_recommendation
        language_usage
        liked/disliked_content
        get_earliest_comment
        get_best_comment
        get_worst_comment
        avg_comment_length
        avg_karma_p_comment
        subreddit_activity
        yearly_posting_activity
        post_types  
        top_posts_by_subreddit
    """
    def __init__(self, username):
        R_User.__init__(self, username)
    
    def top_words(self, size=10, stop_check=True, extra_words=[], subreddit_filter=[]): 
        """ Return top words used at size amounts. """
        def _add(word, collection):
            if word in collection:
                collection[word] += 1
            else:
                collection[word] = 1
                
        def _check(word, collection, stop_check=True, extra_words=[]):
            word_l = word.lower()
            lang = get_language(word_l)
            if stop_check: 
                if word_l in STOPWORDS_DICT[lang] or word_l in extra_words:
                    self.add_to_stop_count()
                else:    
                    _add(word_l, collection)
            else: 
                _add(word_l, collection)
                
        def _add_to_dictionary(word, collection, stop_check=True, extra_words=[]):
            word = ''.join(ch for ch in word if ch not in punc) # removes any other significant punctuation
            if word.isalpha():
                _check(word, collection, stop_check, extra_words=extra_words)
                
        new_collection = dict() 
        for c in self.get_comments(subreddit_filter=subreddit_filter):
            lang = get_language(c.body)
            body = c.body.strip().split()
            for word in body:
                if stop_check:
                    word_l = word.lower()
                    if word_l in STOPWORDS_DICT[lang] or word_l in extra_words:
                        self.add_to_stop_count() 
                    elif any([word.endswith(p) for p in punc]): # checks for ending punctuation.
                        _add_to_dictionary(word[:-1], new_collection, extra_words=extra_words)
                    else:  
                        _add_to_dictionary(word, new_collection, extra_words=extra_words)
                else: 
                    _add_to_dictionary(word,new_collection, stop_check=False)

        if size == 'max':
            size = len(new_collection)

        self.unique_words = len(new_collection)

        # collections returns a tuple. 
        # Built in try-catch to deal with index errors; if size>len(new_collectin);size=len(new_collection) 
        return collections.Counter(new_collection).most_common(size)
    
    def subreddit_recommendation(self, user_selection=None):
        if user_selection:
            return [s.display_name 
                    for s in r.get_subreddit_recommendations(user_selection)]
        else: 
            subreddits = self.get_subreddit_activity()

            # Send subreddit activtiy and add a plus or minus factor
            # to the subreddits based on liked and disliked content. 
            # try:
            #     liked = self.liked_content(raw=True)
            #     disliked = self.disliked_content(raw=True)                
            #     subreddits = self.dict_plus_minus(liked, disliked, subreddits)
            # except Exception:
            #     pass 
            
            rank = sorted([(k,v) for k,v in subreddits.items()], key=lambda tup: tup[1], reverse=True)

            if len(rank) == 0:
                return None 

            top = (r.get_subreddit_recommendations([s[0] for s in rank[:2]]) if len(rank) > 1 
                   else r.get_subreddit_recommendations([rank[0][1]]))
            
            return [t.display_name for t in top]
        
    def language_usage(self):
        """ Must have analyzed User comments before usage. """
        d = {lang: self.dict_values_to_percentage(count, self.comment_count())
             for lang, count in self.lang_usage.items()}
        
        return self.collections_sort(d, key=1, reverse=True) 
        
    def subreddit_activity(self):
        activity = self.get_subreddit_activity()

        # Get total sum. 
        activity_sum = self.dict_values_sum(activity)
            
        d = {k: self.dict_values_to_percentage(v, activity_sum) for k, v in activity.items()}
        return self.collections_sort(d, key=1, reverse=True)

    def yearly_posting_activity(self): 
        def _create_months():
            return [0 for i in range(1, 13)]

        def _add(years, year, month):
            if year in years:
                _month_plus(month, year, years) 
            else:
                years[year] = _create_months()
                _month_plus(month, year, years)

        def _month_plus(month, year, years):
            years[year][month - 1] += 1 

        years = dict()
        
        for c in self.get_comments(): 
            full = self.utc_to_readable(c.created_utc)
            year = self.get_year(full)
            month = self.get_month(full)
            _add(years, int(year), int(month))
            
        return self.collections_sort(years, 0, reverse=True)

    def avg_comment_length(self):
        return self.check_mod_by_zero(self.get_word_count(), self.comment_count())
    
    def avg_karma_p_comment(self):
        return self.check_mod_by_zero(self.get_comment_karma(), self.comment_count())
    
    def avg_karma_p_post(self):
        return self.check_mod_by_zero(sum([p.score for p in self.get_posts()]), self.post_count())
    
    def get_earliest_comment(self):
        count = self.comment_count()
        if count > 0:
            c = self.comments[count]
            return self.utc_to_readable(c.created), c.permalink
    
    def get_best_comment(self):
        return self.best_comment[0], self.check_if_none(self.best_comment[1])

    def get_worst_comment(self):
        return self.worst_comment[0], self.check_if_none(self.worst_comment[1])

    def get_best_post(self):
        return self.best_post[0], self.check_if_none(self.best_post[1])

    def get_worst_post(self):
        return self.worst_post[0], self.check_if_none(self.worst_post[1])

    def percent_edited(self):
        count = sum([1 for c in self.get_comments() if c.edited])
        return round(self.check_mod_by_zero(float(count), self.comment_count()) * 100, 2)

    def account_created(self):
        return self.utc_to_readable(self.get_created())
    
    def post_types(self):
        types = {'text': 0}
        for p in self.get_posts():
            p = p.domain 
            if self.is_text(p):
                types['text'] += 1 
            elif p in types:
                types[p] += 1
            else:
                types[p] = 1
        return self.collections_sort(types, key=1, reverse=True) 
        
    def top_words_by_subreddits(self):
        d = {s: self.top_words(size='max', subreddit_filter=s) for s in self.get_subreddits()}    
        return self.collections_sort(d, key=0, reverse=False)
        
    # Curently unused functions.  
    # Requires selected R_User to allow voting history. 
    # def liked_content(self, raw=False):
    #     liked = self.get_liked_content()
        
    #     return self.content_analysis(liked, raw=raw)
    
    # def disliked_content(self, raw=False):
    #     disliked = self.get_disliked_content()
        
    #     return self.content_analysis(disliked, raw=raw)
    
    #### #### #### #### HELP FUNCTIONS #### #### #### #### #### #### 
    def check_if_none(self, o):
        if isinstance(o, praw.objects.Comment):
            return o.permalink

        if isinstance(o, praw.objects.Submission):
            return o.permalink

    def check_mod_by_zero(self, int1, int2):
        try:
            c = int1 / int2
        except Exception: # zero division
            return 0
        else:
            return c 

    def is_text(self, post):
        return post[:4] == 'self'

    def utc_to_readable(self, time): 
        return datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d')

    def get_month(self, time):
        # Recieves readable utc in Y-M-D form. 
        month = time.split('-')[1]
        if month[0] == '0':
            return month[1:]
        else: 
            return month 
            
    def get_year(self, time):
        return time.split('-')[0]
    
    def date_comment_dict(self):
        return {c: self.utc_to_readable(c.created_utc) for c in self.get_comments()}    
    
    def dict_plus_minus(self, liked, disliked, subreddits):
        for l in liked: 
            if l in subreddits:
                subreddits[l] += 1 
            else: 
                subreddits[l] = 1
        for d in disliked:
            if d in subreddits:
                subreddits[d] -= 1 
            else:
                subreddits[d] = 0 
                
        return subreddits
    
    def dict_values_sum(self, d):
        return sum(d.values())
    
    def dict_values_to_percentage(self, v, total):
        return round(self.check_mod_by_zero(float(v), total) * 100, 2)
            
    def collections_sort(self, items, key, reverse=True):
        return collections.OrderedDict(sorted(items.items(), key=lambda t: t[key], reverse=reverse)) 
    
    def content_analysis(self, content, raw=False): 
        def _add_subreddit(self, content, subreddit):
            sub = subreddit.subreddit.display_name
            if sub in content:
                content[sub] += 1
            else: 
                content[sub] = 1  
        try: 
            subreddits = dict()
            for s in content: 
                _add_subreddit(self, subreddits, s)
            
            total_sum = self.dict_values_sum(subreddits)
            if raw:
                return self.collections_sort(subreddits, key=1, reverse=True)
            else: 
                for k, v in subreddits.items():
                    subreddits[k] = self.dict_values_to_percentage(v, total_sum)
            
                return self.collections_sort(subreddits, key=1, reverse=True) 
                
        except praw.requests.exceptions.HTTPError:
            raise Exception("Forbidden: please change your reddit privacy settings under 'preferences' -> 'make my votes public' to allow vote analysis.")
