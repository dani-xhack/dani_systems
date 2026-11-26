from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='render_seo_article')
def render_seo_article(text):
    lines = escape(text).splitlines()
    out = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if s.startswith('### '):
            out.append(f'<h3 style="color:var(--accent);font-size:1.25rem;margin:1.5rem 0 .6rem">{s[4:]}</h3>')
        elif s.startswith('## '):
            out.append(f'<h2 style="color:var(--accent);font-size:1.45rem;margin:1.8rem 0 .8rem">{s[3:]}</h2>')
        else:
            out.append(f'<p style="margin-bottom:1rem;line-height:1.75">{s}</p>')
    return mark_safe('\n'.join(out))

@register.filter(name='split_tags')
def split_tags(value):
    if not value:
        return []
    return [t.strip() for t in value.split(',') if t.strip()]
