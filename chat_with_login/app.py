from fasthtml.common import *

# sqlite database, built-in approach
db = database('data/uchats.db')

# set up tables
chats, users = db.t.chats, db.t.users

if chats not in db.t:
    users.create(dict(name=str, pwd=str), pk='name')
    chats.create(id=int, title=str, name=str, history=dict, pk='id')

Chat,User = chats.dataclass(),users.dataclass()

# https://www.starlette.io/responses/#redirectresponse
login_redir = RedirectResponse('/login', status_code=303)

# beforeware
def before(req, sess):
    # This sets the `auth` attribute in the request scope, and gets it from the session.
    # The session is a Starlette session, which is a dict-like object which is cryptographically signed,
    # so it can't be tampered with.
    # The `auth` key in the scope is automatically provided to any handler which requests it, and can not
    # be injected by the user using query params, cookies, etc, so it should be secure to use.
    auth = req.scope['auth'] = sess.get('auth', None)
    # If the session key is not there, it redirects to the login page.
    if not auth: return login_redir
    # `xtra` is part of the MiniDataAPI spec. It adds a filter to queries and DDL statements,
    # to ensure that the user can only see/edit their own todos.
    chats.xtra(name=auth)

bware = Beforeware(before, skip=[r'/favicon\.ico', r'/static/.*', r'.*\.css', '/login'])

def _not_found(req, exc): return Titled('Oh no!', Div('We could not find that page :('))

# js imports
markdown_js = """
import { marked } from "https://cdn.jsdelivr.net/npm/marked/lib/marked.esm.js";
import { proc_htmx} from "https://cdn.jsdelivr.net/gh/answerdotai/fasthtml-js/fasthtml.js";
proc_htmx('.markdown', e => e.innerHTML = marked.parse(e.textContent));
"""

# initialize the app itself

app = FastHTML(before=bware,
               htmlkw={"data-theme": "light"},
               # These are the same as Starlette exception_handlers, except they also support `FT` results
               exception_handlers={404: _not_found},
               # PicoCSS is a particularly simple CSS framework, with some basic integration built in to FastHTML.
               # `picolink` is pre-defined with the header for the PicoCSS stylesheet.
               # You can use any CSS framework you want, or none at all.
               hdrs=(picolink,
                     # `Style` is an `FT` object, which are 3-element lists consisting of:
                     # (tag_name, children_list, attrs_dict).
                     # FastHTML composes them from trees and auto-converts them to HTML when needed.
                     # You can also use plain HTML strings in handlers and headers,
                     # which will be auto-escaped, unless you use `NotStr(...string...)`.
                     Style(':root { --pico-font-size: 100%; --pico-font-family: monospace;}'),
                     # Have a look at fasthtml/js.py to see how these Javascript libraries are added to FastHTML.
                     # They are only 5-10 lines of code each, and you can add your own too.
                     SortableJS('.sortable'),
                     # MarkdownJS is actually provided as part of FastHTML, but we've included the js code here
                     # so that you can see how it works.
                     Script(markdown_js, type='module'),)
                )
# We add `rt` as a shortcut for `app.route`, which is what we'll use to decorate our route handlers.
# When using `app.route` (or this shortcut), the only required argument is the path.
# The name of the decorated function (eg `get`, `post`, etc) is used as the HTTP verb for the handler.
rt = app.route

# login page
@rt("/login")
def get():
    # Alternatively, manually call e.g `ft(tag_name, *children, **attrs)`.
    frm = Form(
        # Tags with a `name` attr will have `name` auto-set to the same as `id` if not provided
        Input(id='name', placeholder='Name'),
        Input(id='pwd', type='password', placeholder='Password'),
        Button('login'),
        action='/login', method='post')
    # If a user visits the URL directly, FastHTML auto-generates a full HTML page.
    # However, if the URL is accessed by HTMX, then one HTML partial is created for each element of the tuple.
    # To avoid this auto-generation of a full page, return a `HTML` object, or a Starlette `Response`.
    # `Titled` returns a tuple of a `Title` with the first arg and a `Container` with the rest.
    # See the comments for `Title` later for details.
    return Titled("Login", frm)

# now we need to actually define a login method and handle the data

@dataclass
class Login: name:str; pwd:str

@rt("/login")
def post(login:Login, sess):
    if not login.name or not login.pwd: return login_redir
    # Indexing into a MiniDataAPI table queries by primary key, which is `name` here.
    # It returns a dataclass object, if `dataclass()` has been called at some point, or a dict otherwise.
    try: u = users[login.name]
    # If the primary key does not exist, the method raises a `NotFoundError`.
    # Here we use this to just generate a user -- in practice you'd probably to redirect to a signup page.
    except NotFoundError: u = users.insert(login)
    # This compares the passwords using a constant time string comparison
    # https://sqreen.github.io/DevelopersSecurityBestPractices/timing-attack/python
    if not compare_digest(u.pwd.encode("utf-8"), login.pwd.encode("utf-8")): return login_redir
    # Because the session is signed, we can securely add information to it. It's stored in the browser cookies.
    # If you don't pass a secret signing key to `FastHTML`, it will auto-generate one and store it in a file `./sesskey`.
    sess['auth'] = u.name
    return RedirectResponse('/', status_code=303)

@app.get("/logout")
def logout(sess):
    del sess['auth']
    return login_redir

# and we need a '/' page to redirect to

@rt("/")
def get(auth):
    title = f"Welcome, {auth}!"
    top = Grid(H1(title), Div(A('logout', href='/logout'), style='text-align: right'))

    return Title(title), Container(top)

serve()
