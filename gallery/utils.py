#!/usr/bin/env python

import hashlib
import json
import random
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


def generate_hash():
    """
    Generates a random SHA-1 hash to be used for album share IDs. Returns a hexadecimal string.
    """

    return hashlib.sha1(str(random.getrandbits(256))).hexdigest()