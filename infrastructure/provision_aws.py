import uuid
from botocore.exceptions import ClientError


from services.network_service import (
    NetworkService
)

from services.security_group_service import (
    SecurityGroupService
)

from services.subnet_group_service import (
    DBSubnetGroupService
)

from services.rds_service import (
    RDSService
)

from services.s3_service import (
    S3Service
)

from config.settings import Settings


class InfrastructureProvisioner:

    def __init__(self):

        self.network_service = NetworkService()

        self.security_service = SecurityGroupService()

        self.subnet_service = DBSubnetGroupService()

        self.rds_service = RDSService()

        self.s3_service = S3Service()

    def provision(self):

        print("\nFinding VPC...")

        vpc_id = (
            self.network_service.get_default_vpc()
        )

        print(f"VPC: {vpc_id}")

        print("\nFinding Public Subnets...")

        subnet_ids = (
            self.network_service
            .get_first_three_public_subnets(
                vpc_id
            )
        )

        print(subnet_ids)

        print("\nGetting Public IP...")

        public_ip = (
            self.network_service
            .get_current_public_ip()
        )

        print(public_ip)

        print("\nCreating Security Group...")


        try:

            security_group_id = (
                self.security_service.create_security_group(
                    group_name="ecommerce-rds-sg",
                    description="Ecommerce RDS Security Group",
                    vpc_id=vpc_id
                )
            )

        except ClientError as e:

            if e.response["Error"]["Code"] == "InvalidGroup.Duplicate":

                print(
                    "Security Group already exists."
                )

                security_group_id = (
                    self.security_service.get_security_group_id(
                        "ecommerce-rds-sg"
                    )
                )

            else:
                raise

        print(
            f"Security Group: "
            f"{security_group_id}"
        )

        print(
            "\nAllowing PostgreSQL Access..."
        )

        self.security_service.allow_postgres_access(
            security_group_id,
            public_ip
        )

        print(
            "\nCreating DB Subnet Group..."
        )

        subnet_group_name = (
            "ecommerce-db-subnet-group"
        )

        try:

            self.subnet_service.create_subnet_group(
                subnet_group_name=subnet_group_name,
                subnet_ids=subnet_ids
            )

            print(
                "DB Subnet Group created."
            )

        except ClientError as e:

            if (
                e.response["Error"]["Code"]
                == "DBSubnetGroupAlreadyExists"
            ):

                print(
                    "DB Subnet Group already exists."
                )

                self.subnet_service.get_subnet_group(
                    subnet_group_name
                )

            else:
                raise

        print(
            "\nCreating PostgreSQL RDS..."
        )

        db_identifier = (
            "ecommerce-postgres-db"
        )

        self.rds_service.create_postgres_instance(
            db_identifier=db_identifier,
            db_subnet_group=subnet_group_name,
            security_group_id=security_group_id
        )

        print(
            "\nWaiting for RDS..."
        )

        self.rds_service.wait_until_available(
            db_identifier
        )

        endpoint = (
            self.rds_service.get_endpoint(
                db_identifier
            )
        )

        print(
            f"\nRDS Endpoint: {endpoint}"
        )

        print(
            "\nCreating S3 Bucket..."
        )

        bucket_name = (
            "ecommerce-sales-analytics-890615325018"
        )

        self.s3_service.create_bucket(
            bucket_name
        )

        self.s3_service.create_folder_structure(
            bucket_name
        )

        print(
            f"S3 Bucket: {bucket_name}"
        )

        self.update_env(
            endpoint,
            bucket_name
        )

        print(
            "\nInfrastructure Created Successfully"
        )

    def update_env(
        self,
        db_host,
        bucket_name
    ):

        env_content = f"""
            AWS_REGION={Settings.AWS_REGION}

            DB_HOST={db_host}
            DB_PORT=5432

            DB_NAME={Settings.DB_NAME}
            DB_USER={Settings.DB_USER}
            DB_PASSWORD={Settings.DB_PASSWORD}

            S3_BUCKET={bucket_name}
            """

        with open(".env", "w") as file:

            file.write(
                env_content.strip()
            )


if __name__ == "__main__":

    provisioner = (
        InfrastructureProvisioner()
    )

    provisioner.provision()