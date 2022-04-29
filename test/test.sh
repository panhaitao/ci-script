export VAULT_TOKEN=s.73uKG8Ib1Kcq2SVBPDKulGah
export VAULT_URL=https://vault.onwalk.net
export VAULT_PATH=token
export DEV_ROLE_SECRET=aws-sgc
export OPS_ROLE_SECRET=aws-ops
export PRD_ROLE_SECRET=aws-cn
export CURRENT_ROLE=arn:aws-cn:iam::815347205985:role/TFAdminAccessRole
export CURRENT_PROFILE=sgc-test-user
export S3_SECRET=s3
mkdir -pv /tmp/aws
python3 vault-to-provider-config.py
