import django_tables2 as tables

class ButtonColumn(tables.TemplateColumn):

    def __init__(self, text="", onclick="location.href='#'", title="", condition = '0',gl_icon=None, extra_class="btn-default", **extra):
        glyph_icon = ""
        html_code = ""
        if gl_icon:
            glyph_icon += "<span class='fa fa-%s' aria-hidden='true'></span> " % gl_icon
        html_code += "{% if " + condition + " %}"
        html_code += """<button type="button" class="btn btn-sm %s pull-center" onclick="%s" title="%s"
                data-toggle="tooltip" data-placement="top">%s%s</button>""" \
                                 % (extra_class, onclick, title,glyph_icon, text)
        html_code += "{% endif %}"
        extra['template_code'] = html_code
        super(ButtonColumn, self).__init__(**extra)

class ButtonsColumn(tables.TemplateColumn):

    def __init__(self, btn_list, **extra):
        html_code = """<div class="btn-group btn-group-sm" role="group">"""
        for btn in list(btn_list):
            glyph_icon = extra_class = onclick = text = ""
            condition = '1'
            if 'gl_icon' in btn:
                glyph_icon = "<span class='glyphicon glyphicon-%s' aria-hidden='true'></span> " % btn['gl_icon']
            if 'extra_class' in btn:
                extra_class = btn['extra_class']
            if 'onclick' in btn:
                onclick = btn['onclick']
            if 'text' in btn:
                text = btn['text']
            if 'condition' in btn:
                condition = btn['condition']
            html_code += "{% if " + condition + " %}"
            html_code += """<button type="button" class="btn %s" onclick="%s">%s%s</button>""" \
                         % (extra_class, onclick, glyph_icon, text)
            html_code += "{% endif %}"
        html_code += """</div>"""
        extra['template_code'] = html_code
        super(ButtonsColumn, self).__init__(**extra)        
        
class ImageLinkColumn(tables.TemplateColumn):
    
    def __init__(self,link="#",img=None,**extra):
        extra['template_code']="""<a href="%s"><img src="%s" /></a>""" % (link, img)
        super(ImageLinkColumn, self).__init__(**extra)
        
class ModelDetailLinkColumn(tables.TemplateColumn):

    def __init__(self, **extra):
        extra['template_code'] = """<a href="{{ record.get_absolute_url }}">{{ record }}</a>"""
        if 'accessor' not in extra:
            extra['accessor'] = "id"
        super(ModelDetailLinkColumn, self).__init__(**extra)
        
class IncludeColumn(tables.TemplateColumn):

    def __init__(self, include_name, **extra):
        extra['template_code'] = "{% include '" + include_name + "' %}"
        super(IncludeColumn, self).__init__(**extra)
        
class CssFieldColumn(tables.TemplateColumn):
    
    def __init__(self, field, **extra):
        css_class = "class=%s" % extra.get('class','')
        extra['template_code'] = "<span %s>{{ %s }}</span>" % (css_class,field)
        super(CssFieldColumn, self).__init__(**extra)
        
class LabelIconColumn(tables.TemplateColumn):

    def __init__(self, **extra):
        extra['template_code'] = """{{ record.product }} {% if record.warning %} <img src="/static/assets/img/lot_empty.png" /></a> {% endif %}"""
        #<span class="label label-{{ record.get_state_class }}">{{ record.get_state }}</span>"""
        super(LabelIconColumn, self).__init__(**extra)
        
        
class WaStatusIconColumn(tables.TemplateColumn):

    def __init__(self,area_pk,order_pk, **extra):
        extra['template_code'] = """{{ '12312'  | status_wa }}"""
        #<span class="label label-{{ record.get_state_class }}">{{ record.get_state }}</span>"""
        super(WaStatusIconColumn, self).__init__(**extra)