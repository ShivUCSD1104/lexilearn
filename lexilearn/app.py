from openai import OpenAI
from pypdf import PdfReader
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, resources={r"/generate": {"origins": "*"}})
client = OpenAI(
   api_key=''
)

@app.route('/')
def home():
    return render_template('../worldcourse-free-website-template/index.html')

@app.route('/generate', methods=['POST'])
@cross_origin()
def generate():
  text = []
  txt_response = []
  img_response = []
  book = []

  if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

  pdf_file = request.files['file']

  if pdf_file.filename == '':
      return jsonify({'error': 'No selected file'}), 400

  if not pdf_file:
      return jsonify({'error': 'No file uploaded'}), 400

  pdf_reader = PdfReader(pdf_file)

  for page in pdf_reader.pages:
     book.append(page.extract_text())

  for page in pdf_reader.pages:
    words = page.extract_text().split()
    for i in range(0, len(words), 100):
      para = ' '.join(words[i:i+100])
      text.append(para)

  for txt in text:
    txt_response.append(client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": "Convert this paragraph to a prompt for image generation:"},
        {"role": "user", "content": f"{txt}"}
      ]
    ))
  # print(text[1])
  # print("\n")
  # print(txt_response.choices[0].message.content)
  # print("\n")

  for i in range(len(txt_response)):
    img_response.append(client.images.generate(
      model="dall-e-3",
      prompt=f"Create a colored storyboard WITHOUT ANY SPEECH OR TEXT that illustrates the following paragraph with an appropriate number of frames: {txt_response[i].choices[0].message.content}. Ensure that there is no text in the image.",
      size="1024x1024",
      quality="standard",
      n=1,
    ))

  image_url = list(map(lambda x: x.data[0].url, img_response))
  # image_url = img_response.data[0].url
  print(image_url)

  return jsonify({'image_url': image_url, 'book': book})

if __name__ == '__main__':
    app.run(port=8000, debug=True)

