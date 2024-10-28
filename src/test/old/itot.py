from flask import Flask, request, jsonify
from PIL import Image
import requests
from transformers import BlipProcessor, BlipForConditionalGeneration

# Initialize Flask app
app = Flask(__name__)

# Initialize BLIP model and processor
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")

@app.route('/caption', methods=['POST'])
def caption():
    # Get image URL from POST request
    data = request.json
    img_url = data.get('image_url')
    
    if not img_url:
        return jsonify({"error": "Image URL is required"}), 400

    try:
        # Fetch the image
        response = requests.get(img_url, stream=True)
        response.raise_for_status()  # Ensure we got a successful response
        raw_image = Image.open(response.raw).convert('RGB')
        
        # Conditional image captioning
        text = "a photograph of"
        inputs = processor(raw_image, text, return_tensors="pt")
        out = model.generate(**inputs)
        caption = processor.decode(out[0], skip_special_tokens=True)
        
        # Return the caption
        return jsonify({"caption": caption})

    except requests.RequestException as e:
        return jsonify({"error": "Image fetch error: " + str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Processing error: " + str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    return "Server is up and running!"

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6666, debug=True)  # Enable debug mode
