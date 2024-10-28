import os
import re
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from PyPDF2 import PdfReader
import google.generativeai as genai
from chromadb import Documents, EmbeddingFunction, Embeddings
import chromadb
from typing import List

from .models import Chat  # Import the Chat model

# Replace with your actual API key
GEMINI_API_KEY = "AIzaSyDOKm5KYY6LjLa20IbZg027fQauwyMOKWQ"
genai.configure(api_key=GEMINI_API_KEY)

# Initialize in-memory variables for conversation and DB
conversation_history = []
db = None

# Load PDF content
def load_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text

# Split text into chunks
def split_text(text):
    return [i for i in re.split('\n\n', text) if i.strip()]

# Define the embedding function for ChromaDB
class GeminiEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        model = "models/embedding-001"
        title = "Custom query"
        return genai.embed_content(model=model, content=input, task_type="RETRIEVAL_DOCUMENT", title=title)["embedding"]

# Create a Chroma database with the given documents
def create_chroma_db(documents: List[str], path: str, name: str):
    chroma_client = chromadb.PersistentClient(path=path)
    db = chroma_client.get_or_create_collection(name=name, embedding_function=GeminiEmbeddingFunction())
    for i, d in enumerate(documents):
        db.add(documents=[d], ids=[str(i)])
    return db

# Retrieve the most relevant passages based on the query
def get_relevant_passage(query: str, db, n_results: int):
    results = db.query(query_texts=[query], n_results=n_results)
    return [doc[0] for doc in results['documents']]

# Construct prompt for RAG model
def make_rag_prompt(query: str, relevant_passage: str):
    history_str = "\n".join([f"User: {q}\nBot: {a}" for q, a in conversation_history])
    escaped_passage = relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")
    prompt = f"""You are a helpful and informative bot that answers questions based solely on the provided information.
    Please do not include any information outside of the provided passage or general knowledge. 
    Be sure to respond in a complete sentence, being comprehensive and including all relevant information.
    However, you are talking to a non-technical audience, so break down complex ideas clearly and maintain a friendly tone.

    After your response, please provide at least three follow-up questions related to your answer that the user might find helpful.

    HISTORY:\n{history_str}\n
    QUESTION: '{query}'

    PASSAGE: '{escaped_passage}'

    ANSWER:
    """
    return prompt

# Generate answer using generative AI, including token count metadata
def generate_answer(prompt: str):
    # Ensure the model is initialized only once (consider making it global or module-level)
    model = genai.GenerativeModel("models/gemini-1.5-flash")

    try:
        # Get input token count
        input_token_count_response = model.count_tokens(prompt)
        input_token_count = getattr(input_token_count_response, "total_tokens", 0)

        # Generate response
        response = model.generate_content(prompt)

        # Log relevant responses for debugging
        print("Input Token Count:", input_token_count)
        print("Response Text:", getattr(response, "text", "No response text available"))
        
        # Access token counts directly from usage_metadata
        usage_metadata = getattr(response, "usage_metadata", {})
        output_token_count = getattr(usage_metadata, "candidates_token_count", 0)
        total_token_count = input_token_count + output_token_count

        return response.text, input_token_count, output_token_count, total_token_count

    except Exception as e:
        print(f"Error generating answer: {e}")
        return "An error occurred while generating the answer.", 0, 0, 0


    except Exception as e:
        print(f"Error generating answer: {e}")
        return "An error occurred while generating the answer.", 0, 0, 0






class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # Log in the user and create a session
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)



class ChatView(APIView):
    def post(self, request):
        global conversation_history, db

        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'User not authenticated.'}, status=status.HTTP_403_FORBIDDEN)

        # Handle PDF upload
        if 'pdf_file' in request.FILES:
            uploaded_file = request.FILES['pdf_file']
            pdf_path = "uploaded_file.pdf"
            with open(pdf_path, "wb") as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            # Load and process PDF content
            pdf_text = load_pdf(pdf_path)
            chunked_text = split_text(pdf_text)

            # Create Chroma DB
            db_folder = "chroma_db"
            db_path = os.path.join(os.getcwd(), db_folder)
            db_name = "rag_experiment"
            db = create_chroma_db(chunked_text, db_path, db_name)

            return Response({"message": "PDF uploaded and processed successfully."}, status=status.HTTP_200_OK)

        # Handle user query
        if 'query' in request.data:
            query = request.data.get('query')
            if not query:
                return Response({'error': 'Query is required.'}, status=status.HTTP_400_BAD_REQUEST)

            relevant_text = get_relevant_passage(query, db, n_results=1)
            if relevant_text:
                final_prompt = make_rag_prompt(query, "".join(relevant_text))
                answer, input_token_count, output_token_count, total_token_count = generate_answer(final_prompt)

                # Save query and answer to history
                conversation_history.append((query, answer))

                # Store in Chat model
                Chat.objects.create(user=user, message=query, response=answer)

                # Log token usage
                print(f"Token Usage - Input: {input_token_count}, Output: {output_token_count}, Total: {total_token_count}")

                return Response({
                    'response': answer,
                    'token_usage': {
                        'input_token_count': input_token_count,
                        'output_token_count': output_token_count,
                        'total_token_count': total_token_count
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'No relevant information found for the query.'}, status=status.HTTP_404_NOT_FOUND)

        # Handle new chat
        if 'new_chat' in request.data:
            conversation_history = []
            db = None
            return Response({"message": "New chat started."}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)
