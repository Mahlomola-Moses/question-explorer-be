from google.cloud import storage #pip install google-cloud-storage
from google.oauth2 import service_account

class GoogleService:
    def __init__(self):
        self.books = []
    def read_file_from_gcs(bucket_name, file_name):

        credentials = service_account.Credentials.from_service_account_file(
            't-replica-405819-d66f1c79a8b0.json',
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

        client = storage.Client(credentials=credentials)
    

        
        # Get the bucket
        bucket = client.get_bucket(bucket_name)

        # Get the blob (file) from the bucket
        blob = bucket.blob(file_name)

        # Download the content of the file as bytes
        content = blob.download_as_bytes()

        return content

""" # Example usage
bucket_name = "questionpaps"
file_name = "SEC117V_2023S1_Sick.pdf"

file_content = read_file_from_gcs(bucket_name, file_name, encoding='latin-1')

# Now you can use file_content as needed
print(file_content) """
