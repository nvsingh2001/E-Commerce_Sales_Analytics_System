import boto3
from botocore.exceptions import ClientError
from config.settings import Settings


class SecurityGroupService:
    def __init__(self, ec2_client=None):
        self._ec2_client = ec2_client or boto3.client(
            "ec2", region_name=Settings.AWS_REGION
        )

    def create_security_group(self, group_name: str, description: str, vpc_id: str):
        response = self._ec2_client.create_security_group(
            GroupName=group_name, Description=description, VpcId=vpc_id
        )
        return response["GroupId"]

    def allow_postgres_access(self, security_group_id: str, public_ip: str):
        try:
            self._ec2_client.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[
                    {
                        "IpProtocol": "tcp",
                        "FromPort": int(Settings.DB_PORT),
                        "ToPort": int(Settings.DB_PORT),
                        "IpRanges": [
                            {
                                "CidrIp": f"{public_ip}/32",
                                "Description": "PostgreSQL Access",
                            }
                        ],
                    }
                ],
            )
            print("PostgreSQL ingress rule created.")
        except ClientError as e:
            if e.response["Error"]["Code"] == "InvalidPermission.Duplicate":
                print("PostgreSQL ingress rule already exists.")
            else:
                raise

    def security_group_exists(self, group_name: str):
        response = self._ec2_client.describe_security_groups(
            Filters=[{"Name": "group-name", "Values": [group_name]}]
        )
        return len(response["SecurityGroups"]) > 0

    def get_security_group_id(self, group_name: str):
        response = self._ec2_client.describe_security_groups(
            Filters=[{"Name": "group-name", "Values": [group_name]}]
        )
        return response["SecurityGroups"][0]["GroupId"]
