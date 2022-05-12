import os
import hvac
import json

from jinja2 import Environment, FileSystemLoader

# Capture our current directory
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

    vault_url = os.environ['VAULT_URL']
    vault_token = os.environ['VAULT_TOKEN']

    aws_path = os.environ['AWS_PATH']
    aws_secret = os.environ['AWS_SECRET']

    result_aws=read_vault_vars(vault_url, vault_token, aws_path, aws_secret)

    terraform_temp_vars = {}
    terraform_temp_vars.update( '{'access_key': result_aws['data']['data']['access_key'] }')
    terraform_temp_vars.update( '{'secret_key': result_aws['data']['data']['secret_key'] }')

    ali_path = os.environ['ALI_PATH']
    ali_secret = os.environ['ALI_SECRET']
    result_aws=read_vault_vars(vault_url, vault_token, ali_path, ali_secret)

    terraform_temp_vars.update( '{'ram_dns_access_key': result_ali['data']['data']['ram_dns_access_key'] }')
    terraform_temp_vars.update( '{'ram_dns_secret_key': result_ali['data']['data']['ram_dns_secret_key'] }')
    
    render_template('template/temp-common-variable.yaml', 'terraform/common-variable.yaml', terraform_temp_vars)

    with os.popen('make -C terraform/vpc/aws/ output') as vpc_res_raw:
        vpc_res_json=json.loads( vpc_res_raw.read() )

        vpn_temp_vars = {}
        vpn_temp_vars.update( {'vpn_gw_ip': vpc_res_json['vpn_gw']['value']} )

        render_template('template/temp-inventory.list', 'playbook/inventory.list', vpn_temp_vars)
        render_template('template/temp-wireguard-aws-vpn', 'playbook/todo/wireguard_aws_vpn_gw', vpn_temp_vars)
        render_template('templatet/emp-wireguard-client', 'playbook/todo/wireguard_client', vpn_temp_vars)

    with os.popen('make -C terraform/hosts/aws/ec2/k8s/ output') as k8s_res_exec_raw:
        k8s_res_json=json.loads( k8s_res_exec_raw.read() )

        render_vars = {}
        render_vars.update( {"apiserver": k8s_res_json['k8s-controller_private_ip']['value']} )
        render_vars.update( {"ingress_ip1": k8s_res_json['k8s-worker-1_public_ip']['value']} )
        render_vars.update( {"ingress_ip2": k8s_res_json['k8s-worker-2_public_ip']['value']} )
        render_vars.update( {"ingress_ip2": k8s_res_json['k8s-worker-3_public_ip']['value']} )
        render_vars.update( {"controller1_ip": k8s_res_json['k8s-controller_private_ip']['value']} )
        render_vars.update( {"worker1_ip": k8s_res_json['k8s-worker-1_private_ip']['value']} )
        render_vars.update( {"worker2_ip": k8s_res_json['k8s-worker-2_private_ip']['value']} )
        render_vars.update( {"worker3_ip": k8s_res_json['k8s-worker-3_private_ip']['value']} )

        render_template('template/temp-k8s-aws-bj.list', 'playbook/todo/k8s-aws-bj.list', render_vars)
        render_template('template/temp-k8s-init-config', 'playbook/todo/k8s_cluster_init', render_vars)
        render_template('template/temp-k8s-addon-config', 'playbook/todo/k8s_cluster_add_on_with_remote_helm', render_vars)
