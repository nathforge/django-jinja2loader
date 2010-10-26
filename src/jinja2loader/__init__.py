"""
Jinja2 template loader for Django 1.2 and above. Supports Jinja2 extensions,
and filters written for classic Django templates.

After installing, add jinja2loader.Loader to your project's settings file, e.g:
    >>> TEMPLATE_LOADERS = (
    ...     'jinja2loader.Loader',
    ...     'django.template.loaders.filesystem.Loader',
    ...     'django.template.loaders.app_directories.Loader',
    ... )

You'll probably want to keep the regular Django loaders in there, to not break
apps that have their own templates - such as Django admin.


Settings:
    JINJA2_TEMPLATE_DIRS:
        A tuple of Jinja2 template directories. Defaults to TEMPLATE_DIRS.
    
    JINJA2_EXTENSIONS:
        A tuple of Jinja2 extensions to load - e.g ('jinja2.ext.i18n',)
    
    JINJA2_GLOBALS:
        A dictionary of global variables, passed to every template.
    
    JINJA2_DJANGO_FILTER_LIBRARIES:
        A tuple of Django filter libraries to be registered, given in the
        same format as Django's {% load %} tag - e.g ('humanize',)
    
    JINJA2_USE_DEFAULT_DJANGOFILTERS:
        If True (default), loads Django's built-in filters.


This work is licenced under the Creative Commons Public Domain License. To view
a copy of this licence, visit http://creativecommons.org/licenses/publicdomain/
or send a letter to Creative Commons, 171 Second Street, Suite 300,
San Francisco, California 94105, USA.
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
USE_DEFAULT_DJANGO_FILTERS = getattr(settings, 'JINJA2_USE_DEFAULT_DJANGO_FILTERS', True)


def load_django_filters(filters, library_names, use_default_filters):
    from django.template import get_library, import_library
    
    if use_default_filters:
        library = import_library('django.template.defaultfilters')
        
        if not library:
            raise InvalidTemplateLibrary('Couldn\'t load django.template.defaultfilters')
        
        # Update the dict for filters that don't already exist, i.e
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
    is_usable = jinja2 is not None
    
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATE_DIRS),
        extensions=EXTENSIONS,
        autoescape=True,
    )
    
    load_django_filters(
        env.filters,
        library_names=DJANGO_FILTER_LIBRARIES,
        use_default_filters=USE_DEFAULT_DJANGO_FILTERS,
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

