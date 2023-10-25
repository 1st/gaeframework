from gae import template
from gae.tags import node_rule, BaseNode

register = template.create_template_register()

@register.tag
@node_rule(BaseNode, ("[obj] [attr]", "[obj] [attr] as [varname]"))
def get_attr(self, context):
    '''Return given attribute in given object'''
    obj  = self.get_var(context, self.obj)
    attr = self.get_var(context, self.attr)
    value = getattr(obj, attr)
    if callable(value):
        value = value()
    if hasattr(self, "varname"):
        varname = self.get_var(context, self.varname)
        context[varname] = value
        return ""
    return value
