from flask import Flask, render_template, request, redirect, url_for, make_response
import os, hashlib

# Create an instance of the Flask class
app = Flask(__name__)

def is_file_in_directory(directory, filename):
    filepath = os.path.join(directory, filename)
    return os.path.isfile(filepath)

# Define a route and its corresponding view function
@app.route('/')
def index():
    user = request.cookies.get("user")
    if user != None:
        pass
    else:
        return redirect(url_for("login")), 401
    try:
        folder_path = os.path.join(f"./files/{user}/docs")
        doc_names = os.listdir(folder_path)
    except:
        os.makedirs(f"./files/{user}/docs")
        doc_names = os.listdir(os.path.join(f"./files/{user}/docs"))

    try:
        folder_path = os.path.join(f"./files/{user}/sheets")
        sheet_names = os.listdir(folder_path)
    except:
        os.makedirs(f"./files/{user}/sheets")
        sheet_names = os.listdir(os.path.join(f"./files/{user}/sheets"))

    usr = open(f"users/{user}.usr","r").read()
    print(usr)
    return render_template("home.html", doc_names=doc_names, sheet_names=sheet_names, username=usr)

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        form = request.form
        usr, pswd = form["usr"], form["pswd"]
        user_hash = hashlib.sha256((usr+pswd).encode("utf-8")).hexdigest()
        resp = make_response(redirect("/"))
        resp.set_cookie("user", user_hash)
        with open(f"users/{user_hash}.usr", "w") as f:
            f.write(usr)
            f.close()
        return resp

@app.route("/logout")
def logout():
    resp = make_response(redirect(url_for("login")))
    resp.set_cookie("user", "", expires=0)
    return resp

@app.route('/docs/<filename>')
def view_document(filename):
    user = request.cookies.get("user")
    folder_path = os.path.join(f"./files/{user}/docs")
    file_path = os.path.join(folder_path, filename)

    with open(file_path, 'r') as f:
        content = f.read()

    return render_template('view_doc.html', content=content, filename=filename)

@app.route("/sheets/<filename>")
def view_sheet(filename):
    user = request.cookies.get("user")
    folder_path = os.path.join(f"./files/{user}/sheets")
    file_path = os.path.join(folder_path, filename)

    with open(file_path, "r") as f:
        content = f.read()

    return render_template("view_sheet.html", content=content, filename=filename)

@app.route('/internal/update_file/doc/', methods=['POST'])
def update_file():
    json = request.json  # Get the JSON data from the request body

    content = json["content"]
    name = json["name"]

    user = request.cookies.get("user")

    with open(f"./files/{user}/docs/"+name, "w") as f:
        f.write(content)
    
    return "", 200

@app.route('/internal/update_file/sheet/', methods=['POST'])
def update_sheet():
    json = request.json  # Get the JSON data from the request body

    content = json["content"]
    name = json["name"]
    user = request.cookies.get("user")

    with open(f"./files/{user}/sheets/"+name, "w") as f:
        f.write(content)
    
    return "", 200

@app.route("/create_file", methods=["POST", "GET"])
def create_file():
    if request.method == "GET":
        return render_template("create_new_file.html")
    else:
        fn = request.form["filename"]
        ft = request.form["file_type"]
        user = request.cookies.get("user")
        if ft == ".doc":
            with open(f"./files/{user}/docs/"+fn+ft, "x") as f:
                f.write("")
                f.close()
            return redirect("/docs/" + fn+ft)
        elif ft == ".st":
            with open(f"./files/{user}/sheets/"+fn+ft, "x") as f:
                f.write("")
                f.close()
            return redirect("/sheets/" + fn+ft)
        
@app.route("/delete_file/<filename>")
def delete_file(filename):
    user = request.cookies.get("user")
    if is_file_in_directory(f"./files/{user}/docs/", filename):
        os.remove(f"./files/{user}/docs/{filename}")
    elif is_file_in_directory(f"./files/{user}/sheets/", filename):
        os.remove(f"./files/{user}/sheets/{filename}")
    else:
        return "File not found</br><a href='/'>Go Home</a>"
    
    return redirect(url_for("index"))

# Run the Flask application if this script is executed directly
if __name__ == '__main__':
    app.run(debug=True, port=80)
