#!/usr/bin/env python

import json
from functools import wraps
from django.http import HttpResponse


# From djangosnippets.org
def render_to_json(**jsonargs):
    """
    Renders a JSON response with a given returned instance. Assumes json.dumps() can
    handle the result. The default output uses an indent of 4.

    @render_to_json()
    def a_view(request, arg1, argN):
        ...
        return {'x': range(4)}

    @render_to_json(indent=2)
    def a_view2(request):
        ...
        return [1, 2, 3]

    """
    def outer(f):
        @wraps(f)
        def inner_json(request, *args, **kwargs):
            result = f(request, *args, **kwargs)
            r = HttpResponse(mimetype='application/json')
            if result:
                indent = jsonargs.pop('indent', 4)
                r.write(json.dumps(result, indent=indent, **jsonargs))
            else:
                r.write("{}")
            return r
        return inner_json
    return outer


def missing_keys(dict_, keys):
    """
    Ensures that the given dict has the given keys. Returns either None or a string
    containing the missing keys.

    missing = missing_keys(request.POST, ('username', 'password'))
    if missing:
        ...
    """

    return ", ".join([key for key in keys if key not in dict_]) or None