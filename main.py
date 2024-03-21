import os
from flask import Flask, render_template, flash, request, redirect, send_from_directory, url_for
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
    pages = {}
    for i in range(len(doc)):
        page = doc.load_page(i)
        pix = page.get_pixmap()
        output_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'split_pdfs')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        output_path = os.path.join(output_folder, f"{file}_{i + 1}.png")
        pix.save(output_path)
        pages[i] = output_path
    return pages


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
            convert_to_audio(filename)
            pages = split_pdf(filename)
            return render_template('view_pdf.html', pdf_file=filename, current_page=1, pages=pages)
    return render_template('index.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/page/<filename>/<int:page_num>')
def change_page(filename, page_num):
    output_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'split_pdfs')
    return send_from_directory(output_folder, f"{filename}_{page_num}.png")


@app.route('/view_pdf/<filename>/<int:current_page>', methods=['GET'])
def view_pdf(filename, current_page):
    return render_template('view_pdf.html', pdf_file=filename, current_page=current_page)


@app.route('/previous_page/<filename>/<int:current_page>', methods=['POST'])
def previous_page(filename, current_page):
    previous_page_num = max(current_page - 1, 1)
    return redirect(url_for('view_pdf', filename=filename, current_page=previous_page_num))


@app.route('/next_page/<filename>/<int:current_page>', methods=['POST'])
def next_page(filename, current_page):
    total_pages = len(os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], 'split_pdfs')))
    next_page_num = min(current_page + 1, total_pages)
    return redirect(url_for('view_pdf', filename=filename, current_page=next_page_num))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
