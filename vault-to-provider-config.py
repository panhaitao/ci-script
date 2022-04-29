import os
import ci
import sys
from pathlib import Path

home_dir = str(Path.home())
app_dir = sys.argv[1]


if __name__ == '__main__':

    vault_url         = os.environ['VAULT_URL']
    vault_token       = os.environ['VAULT_TOKEN']
    vault_path        = os.environ['VAULT_PATH']
    dev_role_secret   = os.environ['DEV_ROLE_SECRET']
    ops_role_secret   = os.environ['OPS_ROLE_SECRET']
    prd_role_secret   = os.environ['PRD_ROLE_SECRET']
    curren_role       = os.environ['CURRENT_ROLE']
    curren_profile    = os.environ['CURRENT_PROFILE']
    s3_secret         = os.environ['S3_SECRET']

    terraform_temp_vars = {}

    dev_role_result = ci.read_vault_vars(vault_url, vault_token, vault_path, dev_role_secret)
    dev_role_profile     = dev_role_result['data']['data']['profile']
    dev_role_ak          = dev_role_result['data']['data']['ak']
    dev_role_sk          = dev_role_result['data']['data']['sk']
  
    ops_role_result = ci.read_vault_vars(vault_url, vault_token, vault_path, ops_role_secret)
    ops_role_profile     = ops_role_result['data']['data']['profile']
    ops_role_arn         = curren_role 
    ops_role_src_profile = curren_profile

    terraform_temp_vars.update( { 
    'iam': { 
         'dev': { 'profile': dev_role_profile, 'ak': dev_role_ak, 'sk': dev_role_sk } ,
         'ops': { 'profile': ops_role_profile, 'arn': ops_role_arn, 'source_profile': ops_role_src_profile } 
     } } )


    ci.render_template('template/temp-aws-config', app_dir+'.aws/conf', terraform_temp_vars)
    ci.render_template('template/temp-aws-credentials', app_dir+'.aws/credential', terraform_temp_vars)

    s3_result=ci.read_vault_vars(vault_url, vault_token, vault_path, s3_secret)
    terraform_temp_vars.update( { 's3': {  'bucket': s3_result['data']['data']['bucket'] , 
                                           'key': s3_result['data']['data']['key'] , 
                                           'region': s3_result['data']['data']['region'] ,
                                           'ak': s3_result['data']['data']['ak'] ,  
                                           'sk': s3_result['data']['data']['sk'] 
                                } } )
    ci.render_template('template/temp-provider.tf', app_dir+'provider.tf', terraform_temp_vars)
