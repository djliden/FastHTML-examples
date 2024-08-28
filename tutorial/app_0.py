from fasthtml.common import *

app, rt = fast_app()


@app.get("/")
def hello():
    return (Title("Hello, World!"), Main(H1("Hello, World!"), cls="container"),
            Div(P("Goodbye, World!"), A("About", href="/about"), cls="container"))

@rt("/about")
def get():
    return(Titled("About this Site",
                  P("This is an example site built with FastHTML!"),
                  A("Return Home", href="/")))


serve()
