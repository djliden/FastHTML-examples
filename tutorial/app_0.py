from fasthtml.common import *

app, rt = fast_app()

@app.get("/")
def hello():
    return Titled("Hello, World!")

serve()
