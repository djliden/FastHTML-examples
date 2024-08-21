# source: https://github.com/AnswerDotAI/fasthtml-tut/blob/main/simple01.py
#
# This example was pretty broken. Looks like the fast_app() function api
# changed since this was made, and Page() didn't exist. Changed these. Not
# a very interesting demo regardless.


from fasthtml.common import *

# rt is the route? or how route is specified?
# I get what it *does* but not what it *is*.
#
# This would also return database table(s) if specified.
app, rt = fast_app()

# base route
@rt("/")
def get():
    # http GET call
    contents = Div(
        A('This is a link!', hx_get='/page'),
    )
    return P('Home', contents)
# Doesn't really work, things I still need to figure out...
@rt("/page")
def get():
    contents = Div(
        A('Take me back home!', ht_get='/'),
    )
    return P('Page', contents)
