from flask import Flask, request, send_file, render_template
from flask_cors import CORS
import os
import tempfile
import zipfile
from cairosvg import svg2png, svg2pdf
from PIL import Image

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'svgFile' not in request.files:
        return "No file uploaded", 400

    file = request.files['svgFile']
    sizes = request.form.getlist('sizes')
    format = request.form.get('format', 'png').lower()
    filename_template = request.form.get('filename_template', 'icon_{size}.{format}')
    custom_width = request.form.get('custom_width')
    custom_height = request.form.get('custom_height')

    if format not in ['png', 'jpeg', 'webp', 'ico', 'pdf']:
        return "Unsupported format", 400

    temp_dir = tempfile.mkdtemp()
    svg_path = os.path.join(temp_dir, 'input.svg')
    file.save(svg_path)

    zip_path = os.path.join(temp_dir, 'output.zip')
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        targets = []

        # Custom size
        if custom_width and custom_height:
            try:
                cw = int(custom_width)
                ch = int(custom_height)
                size_label = f"custom_{cw}x{ch}"
                targets.append((cw, ch, size_label))
            except ValueError:
                return "Invalid custom size", 400

        # Preset sizes
        for size in sizes:
            try:
                s = int(size)
                targets.append((s, s, str(s)))
            except ValueError:
                continue

        # Generate output
        for w, h, size_label in targets:
            base_png = os.path.join(temp_dir, f'{size_label}.png')

            if format == 'pdf':
                out_path = os.path.join(temp_dir, f'{size_label}.pdf')
                svg2pdf(url=svg_path, write_to=out_path, output_width=w, output_height=h)
            else:
                svg2png(url=svg_path, write_to=base_png, output_width=w, output_height=h)

                if format == 'png':
                    out_path = base_png
                else:
                    with Image.open(base_png) as im:
                        if format == 'jpeg':
                            im = im.convert("RGB")
                        out_path = os.path.join(temp_dir, f'{size_label}.{format}')
                        im.save(out_path, format.upper())

            # Render final name from template
            ext = format
            final_name = filename_template.replace("{size}", size_label).replace("{format}", ext)
            zipf.write(out_path, arcname=final_name)

    return send_file(zip_path, mimetype='application/zip', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)