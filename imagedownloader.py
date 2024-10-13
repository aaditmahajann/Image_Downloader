
from flask import Flask, render_template, request, send_file
import requests
import os
import zipfile

app = Flask(__name__)

PEXELS_API_KEY = '7m5WnSwWFeWh5aOHvfeI3rmXls6NNStegUMUrwc0DmaQkvtFPUoeYIrN'  # Replace with your actual Pexels API key

def download_images(query, num_images):
    # Construct the Pexels search URL
    search_url = f"https://api.pexels.com/v1/search?query={query}&per_page={num_images}"
    
    headers = {
        'Authorization': PEXELS_API_KEY
    }
    
    # Send a request to the Pexels API
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        
        if not data['photos']:
            return None
        
        image_paths = []
        
        for i, photo in enumerate(data['photos']):
            image_url = photo['src']['original']
            img_data = requests.get(image_url).content
            img_name = f"downloads/{query.replace(' ', '_')}_{i + 1}.jpg"
            with open(img_name, 'wb') as handler:
                handler.write(img_data)
            image_paths.append(img_name)
    except Exception as e:
        return f"Error: {str(e)}"

    return image_paths

def zip_images(image_paths):
    zip_filename = 'downloads/images.zip'
    
    with zipfile.ZipFile(zip_filename, 'w') as zip_file:
        for image_path in image_paths:
            zip_file.write(image_path, os.path.basename(image_path))  # Only store the file name, not the full path

    return zip_filename

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        num_images = int(request.form['num_images'])
        
        try:
            image_paths = download_images(query, num_images)
            if image_paths:
                zip_filename = zip_images(image_paths)
                return send_file(zip_filename, as_attachment=True)
            else:
                return "Failed to download images. Please try again."
        except Exception as e:
            return f"An error occurred: {str(e)}"
    
    return render_template('index.html')

if __name__ == '__main__':
    os.makedirs('downloads', exist_ok=True)
    app.run(debug=True, port=8000)