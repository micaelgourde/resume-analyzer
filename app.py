from flask import Flask, render_template, request, redirect, url_for, session
# render_template is used to render HTML pages in templates folder
# request gives access to data sent by client (uploaded resumes)
# redirect lets you direct the user to a different page 
# url_for lets me generate URL for routes dynamically
# session lets you store small pieces of data per user session

import os

app = Flask(__name__)
# create a new Flask app instance

app.secret_key = "supersecretkey"
#Flask uses this key to secure sessiond ata

app.config["UPLOAD_FOLDER"] = "uploads"
#create a folder to upload resume

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
#makes sure the uploads folder exists on the filesystem, if already exists doesn't throw an error

# "/" tells it to visit the homepage (the root)
# this route can handle GET and POST requests
# in python @app.route before a function tells it when to call it
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # if the user submits information run this block
        if "upload_resume" in request.form:
            resume = request.files.get("resume")
            if not resume:
                return "Please select a resume to upload!"
            resume_path = os.path.join(app.config["UPLOAD_FOLDER"], resume.filename)
            resume.save(resume_path)
            session["resume"] = resume.filename
            return f"Resume {resume.filename} uploaded successfully"
        elif "analyze" in request.form:
            job_desc = request.form.get("job_desc")
            if "resume" not in session or not job_desc:
                return "Please upload a resume and paste a job description before analyzing!"
            saved_resume = session["resume"]
            return f"Analyzing {resume.filename} with pasted job description"
    return render_template("index.html", resume=session.get("resume"))


if __name__ == "__main__":
    app.run(debug=True)




