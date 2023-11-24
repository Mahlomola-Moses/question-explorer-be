import os
from flask import Flask, request
from flask_restful import Resource, Api  # pip install Flask-RESTful
from sentence_transformers import SentenceTransformer, util
import PyPDF2
import re
from nltk.tokenize import sent_tokenize
from google.cloud import storage  # pip install google-cloud-storage
from google.oauth2 import service_account

app = Flask(__name__)
api = Api(app)


class QuestionExtraction(Resource):
    def post(self):
        try:
            
            if os.path.exists("uploaded_file.pdf"):
                os.remove("uploaded_file.pdf")
            if os.path.exists("file_from_google_storage.pdf"):
                os.remove("file_from_google_storage.pdf")
                
                
            if 'file' not in request.files:
                return {'error': 'No selected file'}, 400
            
            file = request.files['file']

            if file.filename == '':
                return {'error': 'No selected file'}, 400

            if file:
                # Save the uploaded file with a different name
                new_file_name = 'uploaded_file.pdf'
                file.save(new_file_name)
            qsList = list_files_in_bucket()
            questions = extract_questions_from_pdf(new_file_name)
            print(len(questions))
            hold=[]
            for file_name in qsList:
                print(file_name)
                read_file_from_gcs("questionpaps", file_name)
                questions2 = extract_questions_from_pdf("file_from_google_storage.pdf")
                print(len(questions2))
                results = compareQsInTheQuestionPapers(questions,questions2,file_name)
                hold.append(results)
            #file_from_google_storage.pdf

            
            # Extract questions from the provided PDF
            #questions = extract_questions_from_pdf("file_from_google_storage.pdf")
            
            return {"questions": hold,"size":"len(questions)"}, 200

        except Exception as e:
            return {"error": str(e)}, 500


class SimilarityCalculation(Resource):
    def post(self):
        try:
            data = request.get_json()
            questions = extract_questions_from_pdf(pdf_path)
            # Extract question and sample_question from the request
            question = data.get("question", None)
            sample_question = data.get("sample_question", None)

            if not question or not sample_question:
                return {"error": "Both question and sample_question are required"}, 400

            # Calculate similarity score between the provided question and the sample question
            similarity_score = calculate_similarity(question, sample_question)

            return {"similarity_score": similarity_score}, 200

        except Exception as e:
            return {"error": str(e)}, 500


def extract_questions_from_pdf(name):
    file_docs = []
    question_paper = ""
    with open(name, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""

        for page in pdf_reader.pages:
            text += page.extract_text()

        text = re.sub(r"\(\d+\)|/\d+/", "", text)
        question_paper += text

    tokens = sent_tokenize(question_paper)
    question_pattern = re.compile(r"Question \d+", re.IGNORECASE)
    question_patterns = question_pattern.findall(question_paper)

    indexes = [question_paper.find(line) for line in question_patterns]

    questions = []
    for ind in indexes:
        end = (
            indexes[indexes.index(ind) + 1]
            if indexes.index(ind) + 1 < len(indexes)
            else None
        )
        substring = question_paper[ind:end].strip()
        questions.append(substring)

    clean_qs = []
    for q in questions:
        substring_to_remove = "Question " + str(questions.index(q) + 1)

        modified_question = q.replace(substring_to_remove, "", 1)
        modified_question = re.sub(r"\s+", " ", modified_question)
        clean_qs.append(modified_question)

    return clean_qs


def calculate_similarity(question, sample_question):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    similarity_score = util.pytorch_cos_sim(
        model.encode([question])[0], model.encode([sample_question])[0]
    )[0][0]
    return similarity_score


def read_file_from_gcs(bucket_name, file_name):
    credentials = service_account.Credentials.from_service_account_file(
        "t-replica-405819-d66f1c79a8b0.json",
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )

    client = storage.Client(credentials=credentials)

    
    bucket = client.get_bucket(bucket_name)

    
    blob = bucket.blob(file_name)

    
    content = blob.download_as_bytes()

    with open("file_from_google_storage.pdf", "wb") as local_file:
        local_file.write(content)
   

def list_files_in_bucket():
    credentials = service_account.Credentials.from_service_account_file(
        "t-replica-405819-d66f1c79a8b0.json",
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )

    client = storage.Client(credentials=credentials)
    bucket = client.get_bucket("questionpaps")

    blobs = bucket.list_blobs()

  
    file_list = [blob.name for blob in blobs]

    return file_list


def compareQsInTheQuestionPapers(questions, questions2,file_name):
    hold =[]
    for question1 in questions:
        
        for question2 in questions2:
            
            similarity = calculate_similarity(question1,question2)
    
            hold.append({"q1": question1, "q2": question2,"similarity": similarity.item(),"questionPaper":file_name})
            
    return hold        
            
            
api.add_resource(QuestionExtraction, "/extract-questions")
api.add_resource(SimilarityCalculation, "/calculate-similarity")

if __name__ == "__main__":
    app.run(debug=True)
