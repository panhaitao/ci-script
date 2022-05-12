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

if __name__ == '__main__':

    aws_region           = os.environ['region']
    aws_count_ak         = os.environ['ak']
    aws_count_sk         = os.environ['sk']
    eks_name             = os.environ['eks_name'] 
    s3_bucket            = os.environ['s3_name']
    chart_repo           = os.environ['chart_repo']
    image_repo           = os.environ['image_repo']
    gitlab_pw            = os.environ['gitlab_pw']
    gitlab_url           = os.environ['gitlab_url']
    gitlab_domain        = os.environ['gitlab_domain']
    gitlab_token         = os.environ['gitlab_token']

    temp_vars = {}

    temp_vars.update( { 
    'region': aws_region,
    'bucket': s3_bucket,
    'count': { 
         'ak': aws_count_ak ,
         'sk': aws_count_sk 
         },
    'eks': { 
         'name': eks_name
        },
    'chart': {
         'repo': chart_repo
        },
    'image': {
         'repo': image_repo
        },
    'gitlab': { 
         'pw': gitlab_pw,
         'url': gitlab_url,
         'token': gitlab_token,
         'domain': gitlab_domain
        }
    } )

    render_template('ci-template/eks-addon', 'deploy-eks-addon', temp_vars)
    render_template('ci-template/gitlab', 'deploy-gitlab', temp_vars)
