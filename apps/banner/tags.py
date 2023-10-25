import logging
from django.template.loader import render_to_string
from gae import template
from gae.tags import node_rule, BaseNode

register = template.create_template_register()

@register.tag
@node_rule(BaseNode, ("[adv_name]",))
def show_banner(self, context):
    '''Show specified banner'''
    try:
        return render_to_string("banner/%s.html" % self.adv_name,
                                context_instance = context)
    except Exception:
        logging.warning("Banner '%s' not found" % self.adv_name)
        return ''