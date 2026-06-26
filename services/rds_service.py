import boto3
from config.settings import Settings


class RDSService:
    def __init__(self, rds_client=None):
        self._rds_client = rds_client or boto3.client(
            "rds", region_name=Settings.AWS_REGION
        )

    def create_postgres_instance(
        self, db_identifier: str, db_subnet_group: str, security_group_id: str
    ):
        response = self._rds_client.create_db_instance(
            DBInstanceIdentifier=db_identifier,
            Engine="postgres",
            EngineVersion="18.1",
            DBInstanceClass="db.t4g.micro",
            AllocatedStorage=20,
            MasterUsername=Settings.DB_USER,
            MasterUserPassword=Settings.DB_PASSWORD,
            DBName=Settings.DB_NAME,
            PubliclyAccessible=True,
            VpcSecurityGroupIds=[security_group_id],
            DBSubnetGroupName=db_subnet_group,
            BackupRetentionPeriod=0,
            MultiAZ=False,
            StorageType="gp3",
        )
        return response

    def wait_until_available(self, db_identifier: str):
        waiter = self._rds_client.get_waiter("db_instance_available")
        waiter.wait(DBInstanceIdentifier=db_identifier)

    def get_endpoint(self, db_identifier: str):
        response = self._rds_client.describe_db_instances(
            DBInstanceIdentifier=db_identifier
        )
        return response["DBInstances"][0]["Endpoint"]["Address"]

    def instance_exists(self, db_identifier: str):
        try:
            self._rds_client.describe_db_instances(DBInstanceIdentifier=db_identifier)
            return True
        except Exception:
            return False
