import os
from ast import literal_eval

QUAY_CLOUD_GOVERNANCE_REPOSITORY = os.environ.get('QUAY_CLOUD_GOVERNANCE_REPOSITORY',
                                                  'quay.io/cloud-governance/cloud-governance')


# available_policies: Run policies in dry_run="yes" mode


def run_cmd(cmd: str):
    """
    This method run the command
    :param cmd:
    :type cmd:
    :return:
    :rtype:
    """
    os.system(cmd)


access_key = os.environ['access_key']
secret_key = os.environ['secret_key']
s3_bucket = os.environ.get('s3_bucket')
account_name = os.environ['account_name']
days_to_delete_resource = os.environ.get('days_to_delete_resource', 14)
LDAP_HOST_NAME = os.environ['LDAP_HOST_NAME']
LOGS = os.environ.get('LOGS', 'logs')
ALERT_DRY_RUN = os.environ.get('ALERT_DRY_RUN', False)
ES_HOST = os.environ['ES_HOST']
ES_PORT = os.environ['ES_PORT']
ADMIN_MAIL_LIST = os.environ.get('ADMIN_MAIL_LIST', '')

# Set es_index if given
ES_INDEX = os.environ.get('ES_INDEX', None)
env_es_index = f'-e es_index={ES_INDEX}' if ES_INDEX else ''


def get_container_cmd(env_dict: dict):
    create_container_envs = lambda item: f'-e {item[0]}="{item[1]}"'
    env_list = ' '.join(list(map(create_container_envs, env_dict.items())))
    container_name = "cloud-governance-poc-haim"
    container_run_cmd = f"""
podman run --rm --name "{container_name}" --net="host" {env_list} {env_es_index} {QUAY_CLOUD_GOVERNANCE_REPOSITORY}
"""
    return container_run_cmd


policies_in_action = ['zombie_cluster_resource',
                      'ip_unattached',
                      # 'zombie_snapshots',
                      'unused_nat_gateway',
                      # 'empty_roles',
                      'unattached_volume']

regions = ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2', 'ap-south-1', 'eu-north-1', 'eu-west-3', 'eu-west-2',
           'eu-west-1', 'ap-northeast-3', 'ap-northeast-2', 'ap-northeast-1', 'ca-central-1', 'sa-east-1',
           'ap-southeast-1', 'ap-southeast-2', 'eu-central-1']

es_doc_type = '_doc'

container_env_dict = {
    "account": account_name, "AWS_DEFAULT_REGION": "us-east-1", "PUBLIC_CLOUD_NAME": "AWS",
    "AWS_ACCESS_KEY_ID": access_key, "AWS_SECRET_ACCESS_KEY": secret_key,
    "dry_run": "yes", "LDAP_HOST_NAME": LDAP_HOST_NAME, "DAYS_TO_DELETE_RESOURCE": days_to_delete_resource,
    "es_host": ES_HOST, "es_port": ES_PORT,
    "MANAGER_EMAIL_ALERT": "False", "EMAIL_ALERT": "False", "log_level": "INFO",
    'DAYS_TO_TAKE_ACTION': days_to_delete_resource, 'ALERT_DRY_RUN': ALERT_DRY_RUN
}


def run_policies(policies: list, dry_run: str = 'yes'):
    for region in regions:
        if s3_bucket:
            container_env_dict.update({"policy_output": f"s3://{s3_bucket}/{LOGS}/{region}"})
        container_env_dict.update({"AWS_DEFAULT_REGION": region, 'dry_run': dry_run})
        for policy in policies:
            container_env_dict.update({"AWS_DEFAULT_REGION": region, 'policy': policy})
            container_cmd = ''
            if policy in ('empty_roles', 's3_inactive', 'unused_access_key') and region == 'us-east-1':
                container_cmd = get_container_cmd(container_env_dict)
            else:
                if policy not in ('empty_roles', 's3_inactive', 'unused_access_key'):
                    container_cmd = get_container_cmd(container_env_dict)
            if container_cmd:
                run_cmd(container_cmd)


# run_cmd(f"echo Running the cloud_governance policies with dry_run=yes")
# run_cmd(f"echo Polices list: {policies_not_action}")
# run_policies(policies=policies_not_action)


run_cmd('echo "Running the CloudGovernance policies with dry_run=no" ')
run_cmd(f"echo Polices list: {policies_in_action}")
run_policies(policies=policies_in_action, dry_run='no')

# run_cmd(f"""echo "Running the tag_iam_user" """)
# run_cmd(
#     f"""podman run --rm --name cloud-governance-poc-haim --net="host" -e account="{account_name}" -e EMAIL_ALERT="False" -e policy="tag_iam_user" -e AWS_ACCESS_KEY_ID="{access_key}" -e AWS_SECRET_ACCESS_KEY="{secret_key}" -e user_tag_operation="update" -e SPREADSHEET_ID="{SPREADSHEET_ID}" -e GOOGLE_APPLICATION_CREDENTIALS="{GOOGLE_APPLICATION_CREDENTIALS}" -v "{GOOGLE_APPLICATION_CREDENTIALS}":"{GOOGLE_APPLICATION_CREDENTIALS}" -e LDAP_HOST_NAME="{LDAP_HOST_NAME}"  -e log_level="INFO" {QUAY_CLOUD_GOVERNANCE_REPOSITORY}""")

# Run the AggMail

# run_cmd(
#     f"""podman run --rm --name cloud-governance-haim --net="host" -e account="{account_name}" -e policy="send_aggregated_alerts" -e AWS_ACCESS_KEY_ID="{access_key}" -e AWS_SECRET_ACCESS_KEY="{secret_key}" -e LDAP_HOST_NAME="{LDAP_HOST_NAME}"  -e log_level="INFO" -e es_host="{ES_HOST}" -e es_port="{ES_PORT}" {env_es_index} -e ADMIN_MAIL_LIST="{ADMIN_MAIL_LIST}" -e ALERT_DRY_RUN="{ALERT_DRY_RUN}" {QUAY_CLOUD_GOVERNANCE_REPOSITORY}""")
