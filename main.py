from flask import Flask, render_template, request, redirect
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

@app.route('/internal/update_file/doc/', methods=['POST'])
def update_file():
    json = request.json  # Get the JSON data from the request body

    content = json["content"]
    name = json["name"]

    print(name)
    print(content)

    with open("files/docs/"+name, "w") as f:
        f.write(content)
    
    return "", 200

@app.route("/create_file", methods=["POST", "GET"])
def create_file():
    if request.method == "GET":
        return render_template("create_new_file.html")
    else:
        fn = request.form["filename"]
        with open("files/docs/"+fn, "x") as f:
            f.write("")
            f.close()
        return redirect("/docs/" + fn)

# Run the Flask application if this script is executed directly
if __name__ == '__main__':
    app.run(debug=True)
