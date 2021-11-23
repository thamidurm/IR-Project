import os
from flask import Flask, request
from search import filtered_search_results

app = Flask(__name__)

@app.route('/')
def index():
    print('tests')
    return '''
        <html>
            <head></head>
            <body>
            <form action="/search" method="get">
                <input type="text" name="q">
                <button>Search</button>
            </form>
            </body>
        </html>
    '''
    
@app.route('/search')
def search():
    query = request.args.get('q')
    return filtered_search_results(query)

if __name__ == '__main__':
    app.run(debug=True)