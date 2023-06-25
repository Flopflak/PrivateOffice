from flask import Flask, render_template, request, redirect, url_for, make_response, send_file
import os, hashlib, json

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

    try:
        groups = json.loads(open("./groups/groups.json", "r").read())
        user_groups = []
        for group in groups:
            user_list = groups[group]
            if user in user_list:
                user_groups.append(group)
    except:
        pass

    usr = open(f"users/{user}.usr","r").read()
    return render_template("home.html", doc_names=doc_names, sheet_names=sheet_names, username=usr, group_names=user_groups)

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
        
@app.route("/user_settings", methods=["POST", "GET"])
def user_settings():
    if request.method == "GET":
        user = request.cookies.get("user")

        username = open(f"./users/{user}.usr", "r").read()

        data = {
            "username": username
        }

        return render_template("user_settings.html", data=data)
    else:
        data = request.json
        try:
            try:
                try:
                    username = data["username"]
                except:
                    print(Exception("Cloud not get username from request"))
                    return "", 500
                try:
                    with open(f"./users/{request.cookies.get('user')}.usr", "w") as f:
                        f.write(username)
                        f.close()
                except:
                    print(Exception("Cloud not write to file"))
                    return "", 500
            except:
                print(Exception("Something went wrong"))
                return "", 500
            return "", 200
        except:
            return "", 500
        
@app.route("/get_user_profile_pic/<user>")
def get_user_profile_pic(user):
    try:
        return send_file(f"./users/{user}.profilepic")
    except:
        return send_file("./static/profile-pic.webp")
        
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

@app.route("/create_group", methods=["GET", "POST"])
def create_group():

    if request.method == "POST":
        name = request.form.get("groupname")

        try:
            os.makedirs(f"./groups/{name}/")
        except:
            return "Group with this name already exists! <a href='/create_group'>Try something different.</a>", 500
        
        json_file = open("./groups/groups.json", "r").read()
        json_data = json.loads(json_file)
        json_data[name] = [request.cookies.get('user')]
        json_file = json.dumps(json_data)
        open("./groups/groups.json", "w").write(json_file)

        os.makedirs(f"./groups/{name}/docs")
        os.makedirs(f"./groups/{name}/sheets")

        return redirect("/group/" + name)

    else:
        return render_template("create_group.html")
    
@app.route("/group/<group>/delete_file/<filename>")
def delete_group_file(filename, group):
    json_data = json.loads(open("./groups/groups.json", "r").read())
    user_list = json_data[group]
    print(user_list)
    if request.cookies.get('user') not in user_list:
        return redirect("/")

    if is_file_in_directory(f"./groups/{group}/docs/", filename):
        os.remove(f"./groups/{group}/docs/{filename}")
    elif is_file_in_directory(f"./groups/{group}/sheets/", filename):
        os.remove(f"./groups/{group}/sheets/{filename}")
    else:
        return "File not found</br><a href='/'>Go Home</a>"
    
    return redirect(url_for("group", group=group))

@app.route("/group/<group>")
def group(group):
    json_data = json.loads(open("./groups/groups.json", "r").read())
    user_list = json_data[group]
    if request.cookies.get('user') not in user_list:
        return redirect("/")
    
    folder_path = os.path.join(f"./groups/{group}/docs")
    doc_names = os.listdir(folder_path)

    folder_path = os.path.join(f"./groups/{group}/sheets")
    sheet_names = os.listdir(folder_path)

    return render_template("group_view.html", group_name=group, username = open(f"users/{request.cookies.get('user')}.usr","r").read(), doc_names=doc_names, sheet_names=sheet_names)

@app.route("/group/<group>/create_file", methods=["POST", "GET"])
def create_group_file(group):
    if request.method == "GET":
        return render_template("create_new_file.html")
    else:
        json_data = json.loads(open("./groups/groups.json", "r").read())
        user_list = json_data[group]
        if request.cookies.get('user') not in user_list:
            return redirect("/")
        
        fn = request.form["filename"]
        ft = request.form["file_type"]
        if ft == ".doc":
            with open(f"./groups/{group}/docs/"+fn+ft, "x") as f:
                f.write("")
                f.close()
            return redirect(f"/group/{group}/docs/" + fn+ft)
        elif ft == ".st":
            with open(f"./groups/{group}/sheets/"+fn+ft, "x") as f:
                f.write("")
                f.close()
            return redirect(f"/group/{group}/sheets/" + fn+ft)

@app.route("/group/<group>/docs/<filename>")
def view_group_doc(group, filename):
    json_data = json.loads(open("./groups/groups.json", "r").read())
    user_list = json_data[group]
    if request.cookies.get('user') not in user_list:
        return redirect("/")
    
    folder_path = os.path.join(f"./groups/{group}/docs")
    file_path = os.path.join(folder_path, filename)

    with open(file_path, 'r') as f:
        content = f.read()

    return render_template('view_group_doc.html', content=content, filename=filename, url=f'/internal/update_group_file/{group}/doc/', group=group)
        
@app.route("/group/<group>/sheets/<filename>")
def view_group_sheet(group, filename):
    json_data = json.loads(open("./groups/groups.json", "r").read())
    user_list = json_data[group]
    if request.cookies.get('user') not in user_list:
        return redirect("/")
    
    folder_path = os.path.join(f"./groups/{group}/sheets")
    file_path = os.path.join(folder_path, filename)

    with open(file_path, 'r') as f:
        content = f.read()

    return render_template('view_group_sheet.html', content=content, filename=filename, url=f'/internal/update_group_file/{group}/sheet/', group=group)
        

@app.route('/internal/update_group_file/<group>/doc/', methods=['POST'])
def update_group_doc(group):
    rjson = request.json  # Get the JSON data from the request body

    json_data = json.loads(open("./groups/groups.json", "r").read())
    user_list = json_data[group]
    if request.cookies.get('user') not in user_list:
        return redirect("/")

    content = rjson["content"]
    name = rjson["name"]

    with open(f"./groups/{group}/docs/"+name, "w") as f:
        f.write(content)
    
    return "", 200

@app.route('/internal/update_group_file/<group>/sheet/', methods=['POST'])
def update_group_sheet(group):
    rjson = request.json  # Get the JSON data from the request body

    json_data = json.loads(open("./groups/groups.json", "r").read())
    user_list = json_data[group]
    if request.cookies.get('user') not in user_list:
        return redirect("/")

    content = rjson["content"]
    name = rjson["name"]

    with open(f"./groups/{group}/sheets/"+name, "w") as f:
        f.write(content)
    
    return "", 200

@app.route("/add_to_group/<group>", methods=["POST"])
def add_to_group(group):

    user_to_add = request.form.get("username")

    users = os.listdir("./users/")
    for user in users:
        displayname = open("./users/"+user, "r").read()
        if displayname == user_to_add:
            json_file = open("./groups/groups.json", "r").read()
            json_data = json.loads(json_file)
            user_list = json_data[group]
            user_list.append(user.split(".")[0])
            json_data[group] = user_list
            json_file = json.dumps(json_data)
            open("./groups/groups.json", "w").write(json_file)

    return redirect("/group/"+group)

# Run the Flask application if this script is executed directly
if __name__ == '__main__':
    app.run(debug=True, port=80)
