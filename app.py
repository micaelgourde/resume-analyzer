# Flask = framework to create the web application
# render_template = used to show HTML pages stored in "templates" folder
# request = allows access to data sent by users (like uploaded files or form input)
# redirect = lets us send the user to a different page
# url_for = dynamically generates the url for a function route 
# session = stores small pieces of data (like resume filename) per user session (keeps track of user_specific info)
from flask import Flask, render_template, request, redirect, url_for, session

import os            # to interact with files/folders on my computer
import pdfplumber    # to read text from pdf files
import spacy         # NLP library to process text and extracted key words

# Loading the the small English NLP model from SpaCy 
# This allows us to analyze text from the resumes and job descriptions
nlp = spacy.load("en_core_web_sm")

# Create a new Flask web app
app = Flask(__name__)

# Flask uses this key to secure session data
app.secret_key = "supersecretkey"

# Tells flask to put uploaded files into a folder called "uploads"
app.config["UPLOAD_FOLDER"] = "uploads"

# Makes sure the "uploads" folder exists on the filesystem
# exist_ok = True means if the file already exists on my computer don't throw an error
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Defining the homepage route ("/" = the homepage/root of the website)
# This route can handle GET and POST requests
# @app.route before a function tells us when the function is called
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST": 
        # If the user clicked the "upload_resume" button
        if "upload_resume" in request.form: 
            # Gets the uploaded file from the form
            # resume is a FileStorage object created by Flask that temporarily repersents the uploaded file 
            # request.files is a dictionary where "resume" is the key 
            resume = request.files.get("resume")
           
            if not resume:
                return "Please select a resume to upload!"
            
            # Creating the full path to save the file
            resume_path = os.path.join(app.config["UPLOAD_FOLDER"], resume.filename)

            # Saves the file to "uploads" folder on your computer 
            resume.save(resume_path)

            # Stores the file name for the session
            # Session is a dictionary where "resume" is the key 
            session["resume"] = resume.filename 

            return f"Resume {resume.filename} uploaded successfully"
        
        # If the user clicked the "analyze" button
        elif "analyze" in request.form:

            #Gets the job description from the form
            job_desc = request.form.get("job_desc")

            if "resume" not in session or not job_desc:
                return "Please upload a resume and paste a job description before analyzing!"

            # Stores the job description for the session
            session["job_desc"] = job_desc

            # Sends the user to the results page 
            return redirect(url_for("results")) 

    # If its just a GET request (opening the page), show the index.html page
    # Passes the current resume filename to the template to be display to the user
    return render_template("index.html", resume = session.get("resume"))

# Defining the results page route 
@app.route("/results")
def results():
    # Gets the resume filename from the session
    resume_filename = session.get("resume")

    if not resume_filename:
        return redirect(url_for("index"))

    # Gets the job description from the session
    job_desc = session.get("job_desc")

    resume_path = os.path.join(app.config["UPLOAD_FOLDER"], resume_filename)

    # Extracts text from the PDF resume
    resume_text = extract_text_from_pdf(resume_path)

    # Compares resume and job description key words 
    results = compare_keywords(resume_text, job_desc)

    # Shows and passes the results to the template to display to the user
    return render_template("results.html", results = result)

# Function to extract all text from a PDF file 
def extract_text_from_pdf(resume):
    text = ""
    # Opens the PDF file
    with pdfplumber.open(resume) as pdf:
        # Goes through each page and extracts text
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
        return text # Returns all the text as a single string

# Function to extract keywords from the text
def extract_keywords(text): 
    # nlp is the SpaCy model loaded earlier
    # Calling nlp(text) tokenizes and analyzes the text splitting it into tokens (words/punctuation)
    # Also attaches helpful info to each token (like part-of-speech, lemma, whether its a stopswords, etc.)
    # doc is a SpaCy item you can loop over, each item is a token
    doc = nlp(text) 

    # token.text.lower() makes all tokens lowercase
    # token.is_alpha is true for tokens that only contain letters 
    # token.is_stop is true for common words (stopwords) that don't carry meaning
    keywords = [token.text.lower() for token in doc if token.is_alpha and not token.is_stop]

    # returns a list of lowercase tokens that only contain letters and no stopwords
    # also removes duplicates by using set() function and then converts back to list 
    return list(set(keywords)) 

# Function to compare keywords from the resume and job description 
def compare_keywords(resume_text, job_text):
    # Gets the set of keywords from both texts 
    resume_keywords = set(extract_keywords(resume_text))
    job_keywords = set(extract_keywords(job_text))

    # Finding out matched and missing keywords 
    # & Gives you the intersection between two sets 
    matched = resume_keywords & job_keywords
    missing = job_keywords - resume_keywords

    # Returns a dictionary with the results  
    return{
        "score": round(len(matched)/len(job_keywords)*100, 2),
        "matched": list(matched),
        "missing": list(missing)
    }

# Runs the Flask if this file is executed directly 
# debug = True means the server will reload automatically when you change the code 
if __name__ == "__main__":
    app.run(debug = True)



