from flask import Flask, render_template
import os

# Create an instance of the Flask class
app = Flask(__name__)

# Define a route and its corresponding view function
@app.route('/')
def hello():
    folder_path = os.path.join("files/docs")
    file_names = os.listdir(folder_path)
    return render_template("home.html", file_names=file_names)

@app.route('/docs/<filename>')
def view_document(filename):
    folder_path = os.path.join('files/docs')
    file_path = os.path.join(folder_path, filename)

    with open(file_path, 'r') as f:
        content = f.read()

    return render_template('view_doc.html', content=content, filename=filename)

# Run the Flask application if this script is executed directly
if __name__ == '__main__':
    app.run(debug=True)
