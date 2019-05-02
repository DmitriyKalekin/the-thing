from quart import Quart
# from flask import Flask


app = Quart(__name__)
app.url_map.strict_slashes = False
app.config['DEBUG'] = True
app.jobs = []





