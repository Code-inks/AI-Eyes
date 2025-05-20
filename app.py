# app.py
# Import necessary libraries
from flask import Flask, request, jsonify, render_template
from PIL import Image  # Used to open and manipulate images
import torch  # PyTorch is a deep learning framework
from transformers import BlipProcessor, BlipForConditionalGeneration  # Hugging Face Transformers library
import os  # For interacting with the file system

# Create a Flask app
app = Flask(__name__)

# Set a folder where uploaded images will be temporarily stored
app.config['UPLOAD_FOLDER'] = 'uploads'

# Make sure the uploads folder exists. If not, create it.
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load BLIP model components:
# - Processor: prepares the image for the model
# - Model: generates text from the image
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# Define the homepage route
@app.route('/')
def home():
    # Render the index.html template (the frontend form)
    return render_template('index.html')

# Define the analyze route that handles image analysis
@app.route('/analyze', methods=['POST'])
def analyze():
    # Check if an image was uploaded
    if 'image' not in request.files:
        # If no image, return an error message as JSON
        return jsonify({'error': 'No image uploaded'}), 400
    
    # Get the uploaded image file
    file = request.files['image']
    
    try:
        # Open the image using PIL (Python Imaging Library)
        # Convert it to RGB format to make sure it works well with the model
        raw_image = Image.open(file.stream).convert('RGB')
        
        # Use the BLIP processor to prepare the image for the AI model
        inputs = processor(raw_image, return_tensors="pt")  # "pt" means PyTorch tensors

        # Ask the AI model to generate a description of the image
        out = model.generate(**inputs, max_new_tokens=50)  # Generate up to 50 words
        
        # Decode the result from the model into readable text
        description = processor.decode(out[0], skip_special_tokens=True)
        
        # Return the generated description as a JSON response
        return jsonify({'description': description})
    
    except Exception as e:
        # If any error occurs during processing, return it as JSON
        return jsonify({'error': str(e)}), 500

# Run the Flask app in development mode when this script is executed directly
if __name__ == '__main__':
    app.run(debug=True)
