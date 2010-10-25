"""
Jinja2 template loader for Django 1.2 and above.


Copyright (C) 2010 Nathan Reynolds

This software is provided 'as-is', without any express or implied
warranty.  In no event will the authors be held liable for any damages
arising from the use of this software.

Permission is granted to anyone to use this software for any purpose,
including commercial applications, and to alter it and redistribute it
freely, subject to the following restrictions:

1. The origin of this software must not be misrepresented; you must not
   claim that you wrote the original software. If you use this software
   in a product, an acknowledgment in the product documentation would be
   appreciated but is not required.
2. Altered source versions must be plainly marked as such, and must not be
   misrepresented as being the original software.
3. This notice may not be removed or altered from any source distribution.

Nathan Reynolds nath@nreynolds.co.uk
"""

from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import loader, TemplateDoesNotExist, InvalidTemplateLibrary

try:
    import jinja2
except ImportError:
    jinja2 = None


TEMPLATE_DIRS = getattr(settings, 'JINJA2_TEMPLATE_DIRS', settings.TEMPLATE_DIRS)
EXTENSIONS = getattr(settings, 'JINJA2_EXTENSIONS', ())
GLOBALS = getattr(settings, 'JINJA2_GLOBALS', {})

DJANGO_FILTER_LIBRARIES = getattr(settings, 'JINJA2_DJANGO_FILTER_LIBRARIES', ())
USE_DEFAULT_FILTERS = getattr(settings, 'JINJA2_USE_DEFAULT_FILTERS', True)


def load_django_filters(filters, library_names, use_default_filters):
    from django.template import get_library, import_library
    
    if use_default_filters:
        library = import_library('django.template.defaultfilters')
        
        if not library:
            raise InvalidTemplateLibrary('Couldn\'t load django.template.defaultfilters')
        
        # Update the filters dict for filters that don't already exist, i.e
        # jinja2's built-in filters.
        filters.update(dict(
            (name, value)
            for (name, value)
            in library.filters.iteritems()
            if name not in filters
        ))
    
    for name in library_names:
        filters.update(get_library(name).filters)


class Template(jinja2.Template):
    def render(self, context):
        context_dict = {}
        for dct in context.dicts:
            context_dict.update(dct)
        return super(Template, self).render(context_dict)


class Loader(loader.BaseLoader):
    if jinja2:
        is_usable = True
    else:
        is_usable = False
    
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATE_DIRS),
        extensions=EXTENSIONS,
        autoescape=True,
    )
    
    load_django_filters(
        env.filters,
        library_names=DJANGO_FILTER_LIBRARIES,
        use_default_filters=USE_DEFAULT_FILTERS,
    )
    
    env.globals.update(GLOBALS)
    
    env.template_class = Template
    
    def load_template(self, template_name, template_dirs=None):
        try:
            template = self.env.get_template(template_name)
            return (template, template.filename,)
        except (jinja2.TemplateNotFound, IOError):
            # Re-throw a TemplateNotFound as a TemplateDoesNotExist.
            # Jinja2 throws an IOError if we pass it a directory instead
            # of a filename.
            raise TemplateDoesNotExist(template_name)

