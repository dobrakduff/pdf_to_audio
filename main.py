import os
from flask import Flask, render_template, flash, request, redirect, send_from_directory
from werkzeug.utils import secure_filename
from pdf_to_audio import pdf_to_audio
import fitz

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'pudge22211'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_audio(file):
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
    file_name = file.replace('.pdf', "")
    output_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'audio', file_name)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    doc = fitz.open(pdf_path)
    for i in range(len(doc)):
        page_text = doc[i].get_text()
        page_output_file = os.path.join(output_folder, f"page_{i}.mp3")
        pdf_to_audio(page_text, page_output_file)

def split_pdf(file):
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
    doc = fitz.open(pdf_path)
    for i in range(len(doc)):
        page = doc.load_page(i)
        pix = page.get_pixmap()
        output_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'split_pdfs')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        output_path = os.path.join(output_folder, f"{file}_{i}.png")
        pix.save(output_path)
    return len(doc)

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            # convert_to_audio(filename)
            total_pages = split_pdf(filename)
            return render_template('view_pdf.html', pdf_file=filename, current_page=1, total_pages=total_pages)
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/page/<filename>/<int:page_num>')
def change_page(filename, page_num):
    return send_from_directory(app.config['UPLOAD_FOLDER'], f"split_pdfs/{filename}_{page_num}.png")

if __name__ == "__main__":
    app.run(debug=True, port=5000)


# попробовать сделать хранение страниц в dict
# сделать функцианал с переходом между страницами