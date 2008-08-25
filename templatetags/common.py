from django import template
from django.conf import settings
import datetime

register = template.Library()

@register.simple_tag
def active(request, pattern):
    import re
    if re.search('^%s/%s' % (request.META['SCRIPT_NAME'], pattern), request.path):
        return 'active'
    return ''


@register.simple_tag
def date_filter(start, end):
    
    today = datetime.date.today()

    last_7 = (today - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    last_90 = (today - datetime.timedelta(days=90)).strftime('%Y-%m-%d')
    last_365 = (today - datetime.timedelta(days=365)).strftime('%Y-%m-%d')


    view_7, view_90, view_365 = False, False, False

    if end == today:
        if start == today - datetime.timedelta(days=7):
            view_7 = True
        if start == today - datetime.timedelta(days=90):
            view_90 = True
        if start == today - datetime.timedelta(days=365):
            view_365 = True

    s = ''

    if view_7:
        s += 'Last 7 Days'
    else:
        s += """<a href="./?start=%s">Last 7 Days</a>""" % last_7
    s += " | "

    if view_90:
        s += "Last 90 Days"
    else:
        s += """<a href="./?start=%s">Last 90 Days</a>""" % last_90
    s += " | "
    if view_365:
        s += "Last 365 Days"
    else:
        s += """<a href="./?start=%s">Last 365 Days</a>""" % last_365


    return s


@register.simple_tag
def yes_no_img(boolean, reversed=False):
    
    if reversed == 'reversed': 
        if boolean:
            boolean = False
        else:
            boolean = True

    if boolean:
        return """<img src="%simg/admin/icon-yes.gif" alt="Active" />""" % settings.MEDIA_URL
    else:
        return """<img src="%simg/admin/icon-no.gif" alt="Not Active"/>""" % settings.MEDIA_URL



@register.tag
def searchform(parser, token):
    try:
        tag_name, post_url = token.split_contents()
    except:
        try:
            tag_name = token.split_contents()
            post_url = '.'
        except:
            raise template.TemplateSyntaxError, "%r tag requires one or no arguments" % token.contents.split()[0]
    return SearchFormNode(post_url)

class SearchFormNode(template.Node):
    def __init__(self, post_url):
        self.post_url = post_url
        
    def render(self, context):
        template_obj = template.loader.get_template('search_form.html')
        context.push()
        context['post_url'] = self.post_url
        output = template_obj.render(context)
        context.pop()
        return output
                                                                                                                                                            
@register.tag
def gen_table(parser, token):
    try:
        tag_name, queryset, template_name = token.split_contents()
    except:
        try:
            tag_name, queryset = token.split_contents()
            template_name = None
        except:
            raise template.TemplateSyntaxError, "%r tag requires one or two arguments" % token.contents.split()[0]
    return QuerySetTableNode(queryset, template_name)


class QuerySetTableNode(template.Node):

    def __init__(self, queryset, template_name):
        self.queryset = template.Variable(queryset)
        self.template_name = template_name
        
    def render(self, context):
        try:
            queryset = self.queryset.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        
        if not self.template_name:
            app_label = queryset.model._meta.app_label
            model_name = queryset.model._meta.verbose_name
            template_name = '%s/%s_table.html' % (app_label, model_name.lower().replace(' ', ''))
        else:
            template_name  = self.template_name
        template_obj = template.loader.get_template(template_name)

        context.push()
        context['object_list'] = queryset
        output = template_obj.render(context)
        context.pop()
        return output
                                                         
