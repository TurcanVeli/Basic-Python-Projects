import json
from translate import Translator
# Load the JSON data from a file
with open('Türkçe.json', 'r') as f:
    data = json.load(f)

translator = Translator(to_lang="tr")
# Iterate over the list of dictionaries and modify the 'label' key
for item in data["translations"]:
    en = item['translation']
    tr = translator.translate(en)
    print(tr)
    item['translation'] = tr

# Save the modified data back to the file
with open('Türkçe.json', 'w', encoding='utf8') as f:
    json.dump(data, f, ensure_ascii=False)
