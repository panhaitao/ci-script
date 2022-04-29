import os
import hvac
from jinja2 import Environment, FileSystemLoader

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

def read_vault_vars(vault_url, vault_token, vault_path, vault_secret):
    client = hvac.Client(url=vault_url,token=vault_token)
    client.is_authenticated()

    client.secrets.kv.v2.configure(
      max_versions=20,
      mount_point=vault_path,
    )

    request = client.secrets.kv.v2.read_secret_version(mount_point=vault_path, path=vault_secret)
    return request

def render_template( template_source, template_result, template_vars ):
    inventory_env      = Environment(loader=FileSystemLoader(THIS_DIR),
                         trim_blocks=True)
    inventory_template = inventory_env.get_template(template_source)
    inventory_output   = inventory_template.render(vars=template_vars)
    with open(template_result, "w+") as f:
        f.write(inventory_output)
