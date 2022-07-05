from django import template
    
register = template.Library()  
    
@register.simple_tag
def my_tag(nombre, apellido):
    return print(nombre,apellido)