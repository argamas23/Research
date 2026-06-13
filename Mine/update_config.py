import json
import os
import re

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.py")
CLEANED_ENTITIES_PATH = os.path.join(OUTPUT_DIR, "cleaned_entities.json")

def main():
    if not os.path.exists(CLEANED_ENTITIES_PATH):
        print("No cleaned_entities.json found. Run aggregate_graph.py first.")
        return

    with open(CLEANED_ENTITIES_PATH, 'r', encoding='utf-8') as f:
        entities = json.load(f)

    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config_content = f.read()

    pattern = r'(ENTITY_TYPE_OVERRIDES\s*=\s*\{)(.*?)(\n\})'
    match = re.search(pattern, config_content, re.DOTALL)
    if not match:
        print("Could not find ENTITY_TYPE_OVERRIDES in config.py")
        return

    prefix = match.group(1)
    dict_body = match.group(2)
    suffix = match.group(3)

    # Find existing keys
    existing_keys = set(re.findall(r'"([^"]+)"\s*:', dict_body))

    new_entries = []
    for ent in entities:
        name = ent['entity']
        etype = ent['type']
        conf = ent['confidence']
        if name not in existing_keys:
            new_entries.append(f'    "{name}": ("{etype}", {conf}),')

    if new_entries:
        updated_dict_body = dict_body
        if not updated_dict_body.endswith('\n') and updated_dict_body.strip():
            updated_dict_body += '\n'
        elif not updated_dict_body.endswith(',\n') and updated_dict_body.strip():
            updated_dict_body += ',\n'
        elif not updated_dict_body.strip():
            updated_dict_body = '\n'
            
        updated_dict_body += '\n'.join(new_entries)
        
        new_config = config_content[:match.start()] + prefix + updated_dict_body + suffix + config_content[match.end():]
        
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            f.write(new_config)
            
        print(f"Added {len(new_entries)} new entities to config.py!")
    else:
        print("No new entities to add to config.py.")

if __name__ == "__main__":
    main()
