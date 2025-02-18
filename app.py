from flask import Flask, render_template, send_from_directory,url_for
import os

app = Flask(__name__)

# Set the directory containing HTML files
HTML_DIR = "templates"

available_pages = {f.split('.')[0]: f for f in os.listdir(HTML_DIR) if f.endswith('.html')}

@app.route('/')
def home():
    return render_template('index.html')  

@app.route('/<page>')
def serve_page(page):
    if page in available_pages:
        return render_template(available_pages[page])
    return "Page not found", 404

if __name__ == '__main__':
    app.run(debug=True)
