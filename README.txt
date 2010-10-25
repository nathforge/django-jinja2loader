Jinja2 template loader for Django 1.2 and above.

Jinja2loader can load Jinja2 extensions, and filters written for classic Django
templates.

After installation, add jinja2loader.Loader to your project's settings file,
e.g:
    >>> TEMPLATE_LOADERS = (
    ...     'jinja2loader.Loader',
    ...     'django.template.loaders.filesystem.Loader',
    ...     'django.template.loaders.app_directories.Loader',
    ... )

You probably want to keep the regular Django loaders in there, so you don't
break apps that have their own templates - such as Django admin.


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

