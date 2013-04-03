import functools

from celery import current_task

def iterit(*args, **kwargs):
    """
    This takes some input (int, string, list, iterable, whatever) and
    makes sure it is an iterable, making it a single item list if not.
    Importantly, it does rational things with strings.

    You can pass it more than one item. Cast is optional.

    def foo(offsets=10):
        offsets = iterit(offsets, cast=int)
        for f in offsets:
            print "Value %s" % (10 + f)

    >>> foo()
    Value 20
    >>> foo(3)
    Value 13
    >>> foo([1,2])
    Value 11
    Value 12
    >>> foo('3')
    Value 13
    >>> foo(('3', 4))
    Value 13
    Value 14

    Also useful this way:
    foo, bar = iterit(foo, bar)
    """
    if len(args) > 1:
        return [iterit(arg, **kwargs) for arg in args]
    return map(kwargs.get('cast', None),
               args[0] if hasattr(args[0], '__iter__') else [args[0], ])


# def wrap_for_chain(f):
#     """ Too much deep magic. """
#     def _wrapper(*args, **kwargs):
#         if current_task.request.callbacks:
#             next_callback = current_task.request.callbacks.pop()
#             def _wrapped_callback(first_arg, *args, **kwargs):
#                 args_list = list(iterit(first_arg)) + args
#                 return next_callback(*args_list, **kwargs)
#             current_task.request.callbacks.insert(0, _wrapped_callback)
#         return f(*args, **kwargs)
#     return _wrapper

class UnwrapMe(object):
    def __init__(self, contents):
        self.contents = contents

    def __call__(self):
        return self.contents

def wrap_for_chain(f):
    """ Too much deep magic. """
    @functools.wraps(f)
    def _wrapper(*args, **kwargs):
        if type(args[0]) == UnwrapMe:
            args = list(args[0]()) + list(args[1:])
        result = f(*args, **kwargs)

        if type(result) == tuple and current_task.request.callbacks:
            return UnwrapMe(result)
        else:
            return result
    return _wrapper
