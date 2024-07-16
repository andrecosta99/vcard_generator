from flask import Flask, request, send_file, render_template, url_for, redirect, flash
import vobject
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Para usar flash messages
UPLOAD_FOLDER = 'vcards'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_next_filename(prefix, folder, extension):
    index = 1
    while True:
        filename = f"{prefix}{index}.{extension}"
        if not os.path.exists(os.path.join(folder, filename)):
            return filename
        index += 1


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate_vcard():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    work_phone = request.form['work_phone']
    home_phone = request.form['home_phone']
    fax = request.form['fax']
    email = request.form['email']
    company = request.form['company']
    job_title = request.form['job_title']
    street = request.form['street']
    city = request.form['city']
    state = request.form['state']
    postal_code = request.form['postal_code']
    country = request.form['country']
    website = request.form['website']

    vcard = vobject.vCard()
    vcard.add('n').value = vobject.vcard.Name(family=last_name, given=first_name)
    vcard.add('fn').value = f"{first_name} {last_name}"

    if work_phone:
        tel = vcard.add('tel')
        tel.value = work_phone
        tel.type_param = 'WORK,VOICE'

    if home_phone:
        tel = vcard.add('tel')
        tel.value = home_phone
        tel.type_param = 'HOME,VOICE'

    if fax:
        tel = vcard.add('tel')
        tel.value = fax
        tel.type_param = 'FAX'

    email_field = vcard.add('email')
    email_field.value = email
    email_field.type_param = 'WORK'

    if company:
        vcard.add('org').value = company

    if job_title:
        vcard.add('title').value = job_title

    if street or city or state or postal_code or country:
        adr = vcard.add('adr')
        adr.value = vobject.vcard.Address(street=street, city=city, region=state, code=postal_code, country=country)
        adr.type_param = 'WORK,PREF'

    if website:
        vcard.add('url').value = website

    vcard.add('version').value = '3.0'

    filename = get_next_filename('vcard', UPLOAD_FOLDER, 'vcf')
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(vcard.serialize())

    flash(f"vCard generated! Link: {url_for('serve_vcard', filename=filename, _external=True)}")
    return redirect(url_for('download_link', filename=filename))


@app.route('/download/<filename>')
def download_link(filename):
    file_url = url_for('serve_vcard', filename=filename, _external=True)
    return render_template('download.html', file_url=file_url, filename=filename)


@app.route('/vcards/<filename>')
def serve_vcard(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename), mimetype='text/vcard', as_attachment=True,
                     download_name=filename)


if __name__ == '__main__':
    app.run(debug=True)
