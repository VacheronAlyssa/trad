from flask import Flask, request, render_template, send_file
import csv
import requests

app = Flask(__name__)

# Clés et paramètres de l'API Microsoft Translator
translator_key = "5727127391ee409bb248b18205058c56"
translator_endpoint = "https://api.cognitive.microsofttranslator.com"

@app.route('/')
def index():
    return render_template('translate.html')

@app.route('/translate', methods=['POST'])
def translate():
    # Obtenir les paramètres du formulaire HTML
    csv_file = request.files.get("csv_file")

    if not csv_file:
        return "Fichier CSV manquant", 400

    # Lire le fichier CSV d'entrée
    csv_data = []
    csv_file.stream.seek(0)
    csv_string = csv_file.stream.read().decode('utf-8')
    csv_reader = csv.reader(csv_string.splitlines())

    header = next(csv_reader)  # Lire l'en-tête
    csv_data.append(header)

    for row in csv_reader:
        if len(row) >= 2:
            key, message = row
        # Vérifier si le message est en français (fr) et le traduire en néerlandais (nl)
        if message and context == 'fr':
            app.logger.info(f"Traduction en cours du message : {message}")
            translated_message = translate_text(message, 'fr', 'nl')
            app.logger.info(f"Message traduit : {translated_message}")
            row[1] = translated_message
        csv_data.append(row)

    # Écrire les données traduites dans un nouveau fichier CSV
    output_filename = "translated.csv"
    with open(output_filename, mode="w", newline="", encoding="utf-8") as output_file:
        csv_writer = csv.writer(output_file)
        csv_writer.writerows(csv_data)

    return send_file(output_filename, as_attachment=True)

def translate_text(text, from_lang, to_lang):
    path = "/translate"
    constructed_url = f"{translator_endpoint}{path}"

    params = {
        "api-version": "3.0",
        "from": from_lang,
        "to": to_lang,
    }

    headers = {
        "Ocp-Apim-Subscription-Key": translator_key,
        "Content-type": "application/json",
    }

    body = [{"text": text}]

    response = requests.post(constructed_url, params=params, headers=headers, json=body)
    response_data = response.json()

    if response.ok and response_data and "translations" in response_data[0]:
        return response_data[0]["translations"][0]["text"]
    else:
        app.logger.error(f"La traduction a échoué pour le texte : {text}")
        return text

if __name__ == "__main__":
    app.run(debug=True)
