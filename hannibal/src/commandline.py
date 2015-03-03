import inspect, StringIO

class Struct(object): pass

def expose_to_shell(name=None):
    '''Decorator that marks a function as suitable for use via command-line.

    name => By default, the command-line will lets users call the function
            by its name. If this is unseemly, you can specify an alternate
            name. Strictly optional.

    The returned function will have 2 additional properties attached to it:

    _exposed_to_shell = the name the command-line attaches to this function

    _exposed_positional_args = the list of positional arguments that the 
        wrapped function takes. This is used for things like displaying 
        help text.
    '''
    def wrap(func):
        def call(*args):
            return func(*args)
        call._exposed_to_shell = name
        call._exposed_positional_args = inspect.getargspec(func)[0]
        call.__doc__ = func.__doc__
        call.__module__ = func.__module__
        return call
    return wrap

def build(objdict):
    '''Looks for all of the functions in _objdict_ that are marked as exposed
    to the command line, and returns a dictionary mapping:

    function name => (name, args, function, callsite help, usage information)
    '''
    def format(obj):
        name = obj._exposed_to_shell
        if name is None:
            name = obj.func_name
        argnames = obj._exposed_positional_args
        callspec = " ".join(argnames)
        usage = obj.func_doc
        metadata = Struct()
        metadata.name, metadata.args, metadata.func, metadata.callspec, metadata.usage = name, argnames, obj, callspec, usage
        return name, metadata

    def is_exposed(obj):
        return hasattr(obj, "_exposed_to_shell")

    return dict([format(obj) for obj in objdict.values() if is_exposed(obj)])

def format_cmdlist(cli):
    '''Returns a string that represents "usage" information for all the 
    command-line-accessible functions

    cli => data structure returned from call to "build()"
    '''
    s = StringIO.StringIO()
    print >>s, "Available commands:"
    print >>s
    for k in sorted(cli.keys()):
        print >>s, "  %-20s%s" % (k, cli[k].usage.splitlines()[0])
    print >>s
    print >>s, "(use 'help <command>' for more detailed help)"
    return s.getvalue()

def format_cmd_help(metadata):
    '''Display usage information for a specific command

    metadata => a value from a "cli" object returned by "build()"
    '''
    s = StringIO.StringIO()
    print >>s, "Usage:", metadata.name, metadata.callspec
    print >>s
    for line in metadata.usage.splitlines():
        print >>s, "  %s" % line
    return s.getvalue()
