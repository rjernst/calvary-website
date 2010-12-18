import logging

from google.appengine.ext import db, webapp
from google.appengine.api import users
from django.utils import simplejson as json

class Blog(db.Model):
    owner = db.UserProperty()
    name = db.StringProperty()

class Article(db.Model):
    """An article is a blog entry. Each entry, along with data to be 
       displayed, has a list of tags the entry falls under. """
    blog = db.ReferenceProperty(Blog, required=True)
    title = db.StringProperty()
    body = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    draft = db.BooleanProperty(default=True)
    tags = db.ListProperty(db.Category)

class Tag(db.Model):
    """Tags represent categories.  Each tag keeps a count of how
       many articles use that tag. The key_name is the tag name"""
    blog = db.ReferenceProperty(Blog)
    count = db.IntegerProperty(default=0)

def update_tags(article, tags, action):
    """Saves an article and updates tag counters"""
    
    new_tags = [t for t in tags if t not in article.tags]
    old_tags = [t for t in article.tags if t not in tags]
    article.tags = tags
    action(article)

    for t in new_tags:
        update_tag(article.blog, t, True)
    for t in old_tags:
        update_tag(article.blog, t, False)
        
    return article.key().id()

def update_tag(blog, tag, incr):
    """Retrieves a tag or creates it, and increments or decrements the count"""
    t = Tag.get_by_key_name(tag, parent=blog)
    if t is None:
        t = Tag(key_name=tag, blog=blog, parent=blog)

    if incr:
        t.count += 1
    else:
        t.count -= 1
    t.put()    

_article_attrs = ['id', 'title', 'body', 'created', 'updated', 'draft', 'tags']
_time_format = '%Y-%m-%dT%H:%M:%S'
def articles_to_json(articles, attrs):
    buf = []
    for a in articles:
        d = {}
        # TODO: this is probably slow, figure out better way to find which
        # attrs should be output
        if 'id' in attrs:
            d['id'] = a.key().id()
        if 'title' in attrs:
            d['title'] = a.title
        if 'body' in attrs:
            d['body'] = a.body
        if 'created' in attrs:
            d['created'] = a.created.strftime(_time_format)
        if 'updated' in attrs:
            d['updated'] = a.updated.strftime(_time_format)
        if 'draft' in attrs:
            d['draft'] = a.draft
        if 'tags' in attrs:
            d['tags'] = a.tags
            
        buf.append(d)

    return json.dumps(buf)
 
class ArticlesHandler(webapp.RequestHandler):

    def get(self):
        """Retrieves blog articles.

        The following get parameters are used:
        id - identifier for the article to retrieve
        tags - a comma separated list of tags to restrict results to
        max-results - maximum number of results to return, default of 10 
        sort-by - how to sort the results. valid values are 
               ["created", "updated"], defaults to "updated".
        sort-order - order to sort by, valid values are ["asc", "desc"].
                     default is "desc" (newest first)
        attributes - comma separated list of attributes to return.
                     if not specified, defaults to all attributes

        The articles are returned using the following JSON format:
        {
            "id": Article.key().id(),
            "title": Article.title,
            "body": Article.body, 
            "created": Article.created.strftime(FORMAT),
            "updated": Article.updated.strftime(FORMAT),
            "draft": Article.draft,
            "tags": ["tag1", "tag2", ...]
        }

        Dates above use the FORMAT: %Y-%m-%dT%H:%M:%S
        """
        logging.info("GetArticle: %s", self.request.arguments())
        id = self.request.get('id')
        tags = self.request.get('tags')
        max_results = self.request.get('max-results', '10')
        sort_by = self.request.get('sort-by', 'updated')
        sort_order = self.request.get('sort-order', 'desc').upper()

        articles = []
        if id:
            # get the 1 result
            user = users.get_current_user()
            # TODO: add login decorator
            if not user:
                self.redirect(users.create_login_url())
                return
            blog = Blog.get_or_insert(key_name='test', name='test', owner=user)
            a = Article.get_by_id(int(id), blog)
            if a:
                articles.append(a)
        else:
            clauses = ''
            args = {}
            if tags:
                clauses = 'WHERE tags IN :tags'
                args['tags'] = tags.split(',')
            
            q = ['SELECT * FROM Article', clauses, 
                 'ORDER BY', sort_by, sort_order, 
                 'LIMIT', max_results]
            logging.info('Running query: %s', ' '.join(q))
            articles = db.GqlQuery(' '.join(q), **args)

        attrs = self.request.get('attributes')
        if attrs:
            attrs = attrs.split(',')
        else:
            attrs = _article_attrs
            
        self.response.out.write(articles_to_json(articles, attrs));

    def post(self):
        """Creates a new blog article.

        The following form arguments are used:
        title (mandatory) - title of the article
        body (mandatory) - content of the article, html or plaintext
        tags - comma separated list of tags    
        """
        logging.info("CreateArticle: %s", self.request.arguments())
        # TODO: validate syntax/existence of pieces on front end
        title = self.request.get('title')
        body = self.request.get('body')
        user = users.get_current_user()
        # TODO: add login decorator
        if not user:
            self.redirect(users.create_login_url())
            return
        blog = Blog.get_or_insert(key_name='test', name='test', owner=user)
        article = Article(parent=blog, blog=blog, title=title, body=body) 

        tags = self.request.get('tags', '')
        tags = [db.Category(t.strip()) for t in tags.split()]
        id = db.run_in_transaction(update_tags, article, tags, Article.put)
        self.response.out.write('{"id":"%s"}' % id);

    def put(self):
        """Saves changes to a blog article.

        The following form arguments are used:
        id (mandatory) - identifier for article to delete
        title - title of the article
        body - content of the article, html or plaintext
        tags - comma separated list of tags
        """
        logging.info("SaveArticle: %s", self.request.arguments())
        id = self.request.get('id')
        user = users.get_current_user()
        # TODO: add login decorator
        if not user:
            self.redirect(users.create_login_url())
            return
        blog = Blog.get_or_insert(key_name='test', name='test', owner=user)
        article = Article.get_by_id(int(id), parent=blog)
        
        title = self.request.get('title')
        if title:
            article.title = title
        body = self.request.get('body')
        if body:
            article.body = body
        tags = self.request.get('tags', '')
        tags = [db.Category(t.strip()) for t in tags.split()]
        id = db.run_in_transaction(update_tags, article, tags, Article.save)
        self.response.out.write('{"id":"%s", "status":"updated"}' % id);

    def delete(self):
        """Deletes a blog article.

        The following form arguments are used:
        id (mandatory) - identifier for article to delete
        """
        logging.info("DeleteArticle: %s", self.request.arguments())
        id = self.request.get('id')
        user = users.get_current_user()
        # TODO: add login decorator
        if not user:
            self.redirect(users.create_login_url())
            return
        blog = Blog.get_or_insert(key_name='test', name='test', owner=user)
        article = Article.get_by_id(int(id), parent=blog)
        id = db.run_in_transaction(update_tags, article, [], Article.delete)
        self.response.out.write('{"id":"%s", "status":"deleted"}' % id);

class TagsHandler(webapp.RequestHandler):

    def get(self):
        """Retrieves a summary count of articles associated with tags.
    
        The tags are returned using the following JSON format:
        {
            "tag1": Tag.count,
            "tag2": Tag.count,
            ...
        }
        """
        logging.info("SummarizeTags: %s", self.request.arguments())
        user = users.get_current_user()
        # TODO: add login decorator
        if not user:
            self.redirect(users.create_login_url())
            return
        blog = Blog.get_or_insert(key_name='test', name='test', owner=user)
        
        tags = Tag.gql('WHERE blog = :1', blog)
        j = json.dumps(dict([(t.key().name(), t.count) for t in tags]))
        self.response.out.write(j)

app = webapp.WSGIApplication([
    ('/data/blog/articles', ArticlesHandler)
    ('/data/blog/tags', TagsHandler)
], debug=True)
def main(): run_wsgi_app(app)
if __name__ == '__main__': main()
