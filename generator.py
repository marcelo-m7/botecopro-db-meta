import yaml, os
from jinja2 import Environment, FileSystemLoader

BASE = os.path.dirname(__file__)
env = Environment(loader=FileSystemLoader(os.path.join(BASE, 'templates')))

def load_entities(path):
    entities = []
    for root, dirs, files in os.walk(path):
        for fn in files:
            if fn.endswith('.yaml'):
                entities.append(yaml.safe_load(open(os.path.join(root, fn))))
    return entities

def render_template(name, ctx):
    t = env.get_template(name)
    return t.render(ctx)

if __name__ == '__main__':
    schema_dir = os.path.join(BASE, 'db-meta', 'schemas')
    entities = load_entities(schema_dir)
    out_dir = os.path.join(BASE, 'generated')
    os.makedirs(out_dir, exist_ok=True)
    for e in entities:
        ctx = {'entity': e}
        # Render python model
        p = render_template('python_sqlmodel.j2', ctx)
        open(os.path.join(out_dir, f"{e.get('entity')}_model.py"), 'w').write(p)
        # Render SQL
        s = render_template('postgres_table.j2', ctx)
        open(os.path.join(out_dir, f"{e.get('entity')}_table.sql"), 'w').write(s)
    print('Generated', len(entities), 'models')
