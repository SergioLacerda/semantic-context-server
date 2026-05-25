import pytest

from tests.contracts.framework.validator import ArchitectureValidator


@pytest.mark.contract
async def test_container_ports(container):
    campaign = await container.campaigns.get("c1")
    ArchitectureValidator().validate_container(campaign)


@pytest.mark.contract
async def test_storage_ports(container_with_storage):
    await ArchitectureValidator().validate_storage(container_with_storage)


@pytest.mark.contract
async def test_port_coverage(container):
    campaign = await container.campaigns.get("c1")
    ArchitectureValidator().validate_coverage(campaign)


@pytest.mark.contract
async def test_explicit_ports(container):
    campaign = await container.campaigns.get("c1")
    ArchitectureValidator().validate_explicit(campaign)
