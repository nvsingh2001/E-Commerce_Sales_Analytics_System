import boto3
import requests
from config.settings import Settings


class NetworkService:
    def __init__(self, ec2_client=None):
        self._ec2_client = ec2_client or boto3.client(
            "ec2", region_name=Settings.AWS_REGION
        )

    def get_default_vpc(self):
        response = self._ec2_client.describe_vpcs(
            Filters=[{"Name": "isDefault", "Values": ["true"]}]
        )
        vpcs = response["Vpcs"]
        if not vpcs:
            raise Exception("Default VPC not found")
        return vpcs[0]["VpcId"]

    def get_public_subnets(self, vpc_id: str):
        response = self._ec2_client.describe_subnets(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )
        public_subnets = []
        for subnet in response["Subnets"]:
            if subnet.get("MapPublicIpOnLaunch", False):
                public_subnets.append(subnet["SubnetId"])
        return public_subnets

    def get_current_public_ip(self):
        response = requests.get("https://api.ipify.org")
        return response.text

    def get_first_three_public_subnets(self, vpc_id: str):
        subnets = self.get_public_subnets(vpc_id)
        return subnets[:3]
