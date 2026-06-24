import boto3
from botocore.exceptions import ClientError
from config.settings import Settings


class DBSubnetGroupService:

    def __init__(self):

        self.rds_client = boto3.client(
            "rds",
            region_name=Settings.AWS_REGION
        )

    def create_subnet_group(
        self,
        subnet_group_name: str,
        subnet_ids: list[str]
    ):

        try:

            response = self.rds_client.create_db_subnet_group(
                DBSubnetGroupName=subnet_group_name,
                DBSubnetGroupDescription="Ecommerce Sales Analytics DB Subnet Group",
                SubnetIds=subnet_ids
            )

            return response

        except Exception as e:

            print(
                f"Error creating subnet group: {e}"
            )

            raise

    def subnet_group_exists(
        self,
        subnet_group_name: str
    ):

        try:

            self.rds_client.describe_db_subnet_groups(
                DBSubnetGroupName=subnet_group_name
            )

            return True

        except Exception:

            return False
        
        
    def get_subnet_group(
        self,
        subnet_group_name: str
    ):

        response = self.rds_client.describe_db_subnet_groups(
            DBSubnetGroupName=subnet_group_name
        )

        return response["DBSubnetGroups"][0]