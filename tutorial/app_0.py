from fasthtml.common import *

app, rt = fast_app()


@app.get("/")
def hello():
    return (Title("Hello, World!"), Main(H1("Hello, World!"), cls="container"),
            Div(P("Goodbye, World!"), cls="container"))


serve()
