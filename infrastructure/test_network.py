# infrastructure/test_network.py

from services.network_service import (
    NetworkService
)

network = NetworkService()

vpc_id = network.get_default_vpc()

print(vpc_id)

print(
    network.get_public_subnets(
        vpc_id
    )
)

print(
    network.get_current_public_ip()
)