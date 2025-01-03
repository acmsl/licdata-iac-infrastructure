# vim: set fileencoding=utf-8
"""
org/acmsl/iac/licdata/infrastructure/azure/update_azure_infrastructure_with_pulumi.py

This script defines the UpdateAzureInfrastructureWithPulumi class.

Copyright (C) 2024-today acmsl/licdata-iac-infrastructure

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from .functions_package import FunctionsPackage
from .functions_deployment_slot import FunctionsDeploymentSlot
from .licdata_web_app import LicdataWebApp
from org.acmsl.iac.licdata.infrastructure import UpdateInfrastructureWithPulumi
from pulumi import Output
from pythoneda.shared import Event, EventEmitter
from pythoneda.shared.iac.events import InfrastructureUpdateRequested
from pythoneda.shared.iac.pulumi.azure import (
    AppInsights,
    AppServicePlan,
    BlobContainer,
    ContainerRegistry,
    DnsRecord,
    DnsZone,
    DockerPullRoleAssignment,
    DockerPullRoleDefinition,
    FunctionStorageAccount,
    Outputs,
    PublicIpAddress,
    ResourceGroup,
    WebApp,
)
from typing import Dict


class UpdateAzureInfrastructureWithPulumi(UpdateInfrastructureWithPulumi):
    """
    Azure-specific Pulumi implementation of Licdata infrastructure stacks.

    Class name: UpdateAzureInfrastructureWithPulumi

    Responsibilities:
        - Use Azure-specific Pulumi stack as Licdata infrastructure stack.

    Collaborators:
        - org.acmsl.licdata.infrastructure.UpdateInfrastructureWithPulumi
    """

    def __init__(self, event: InfrastructureUpdateRequested):
        """
        Creates a new UpdateAzureInfrastructureWithPulumi instance.
        :param event: The request.
        :type event: pythoneda.shared.iac.events.InfrastructureUpdateRequested
        """
        self._resource_group = None
        self._function_storage_account = None
        self._app_service_plan = None
        self._function_app = None
        self._public_ip_address = None
        self._dns_zone = None
        self._dns_record = None
        self._blob_container = None
        self._functions_package = None
        self._container_registry = None
        self._webapp_deployment_slot = None
        self._app_insights = None
        super().__init__(event)

    @classmethod
    def instantiate(cls):
        """
        Creates an instance.
        :return: The new instance.
        :rtype: pythoneda.iac.pulumi.azure.UpdateAzureInfrastructureWithPulumiFactory
        """
        raise InvalidOperationError(
            "Cannot instantiate UpdateAzureInfrastructureWithPulumi directly"
        )

    @property
    def resource_group(self) -> ResourceGroup:
        """
        Retrieves the Azure Resource Group.
        :return: Such Resource Group.
        :rtype: ResourceGroup
        """
        return self._resource_group

    @property
    def function_storage_account(self) -> FunctionStorageAccount:
        """
        Retrieves the Azure Function Storage Account.
        :return: Such Function Storage Account.
        :rtype: pythoneda.iac.pulumi.azure.FunctionStorageAccount
        """
        return self._function_storage_account

    @property
    def app_service_plan(self) -> AppServicePlan:
        """
        Retrieves the Azure App Service Plan.
        :return: Such App Service Plan.
        :rtype: pythoneda.iac.pulumi.azure.AppServicePlan
        """
        return self._app_service_plan

    @property
    def public_ip_address(self) -> PublicIpAddress:
        """
        Retrieves the Azure Public IP Address.
        :return: Such Public IP Address.
        :rtype: pythoneda.iac.pulumi.azure.PublicIpAddress
        """
        return self._public_ip_address

    @property
    def dns_zone(self) -> DnsZone:
        """
        Retrieves the Azure DNS Zone.
        :return: Such DNS Zone.
        :rtype: pythoneda.iac.pulumi.azure.DnsZone
        """
        return self._dns_zone

    @property
    def dns_record(self) -> DnsRecord:
        """
        Retrieves the Azure DNS Record.
        :return: Such DNS Record.
        :rtype: pythoneda.iac.pulumi.azure.DnsRecord
        """
        return self._dns_record

    @property
    def blob_container(self) -> BlobContainer:
        """
        Retrieves the Azure Blob Container.
        :return: Such Blob Container.
        :rtype: pythoneda.iac.pulumi.azure.BlobContainer
        """
        return self._blob_container

    @property
    def functions_package(self) -> FunctionsPackage:
        """
        Retrieves the Azure Functions Package.
        :return: Such Functions Package.
        :rtype: pythoneda.iac.pulumi.azure.FunctionsPackage
        """
        return self._functions_package

    @property
    def webapp_deployment_slot(self) -> FunctionsDeploymentSlot:
        """
        Retrieves the Azure Functions Deployment Slot.
        :return: Such Functions Deployment Slot.
        :rtype: pythoneda.iac.pulumi.azure.FunctionsDeploymentSlot
        """
        return self._webapp_deployment_slot

    @property
    def app_insights(self) -> AppInsights:
        """
        Retrieves the Azure App Insights instance.
        :return: Such instance.
        :rtype: pythoneda.iac.pulumi.azure.AppInsights
        """
        return self._app_insights

    @property
    def container_registry(self) -> ContainerRegistry:
        """
        Retrieves the Azure Container Registry instance.
        :return: Such instance.
        :rtype: pythoneda.iac.pulumi.azure.ContainerRegistry
        """
        return self._container_registry

    def declare_infrastructure(self):
        """
        Creates the infrastructure.
        """
        self._resource_group = ResourceGroup(
            self.event.stack_name, self.event.project_name, self.event.location
        )

        self._function_storage_account = FunctionStorageAccount(
            self.event.stack_name,
            self.event.project_name,
            self.event.location,
            self._resource_group,
        )

        self._app_service_plan = AppServicePlan(
            self.event.stack_name,
            self.event.project_name,
            self.event.location,
            None,
            None,
            None,
            None,
            None,
            self._resource_group,
        )

        # self._public_ip_address = PublicIpAddress(self.stack_name, self.project_name, self.location, self._resource_group)
        # self._dns_zone = DnsZone(self.stack_name, self.project_name, self.location, self._resource_group)
        # self._dns_record = DnsRecord(
        #    self._public_ip_address,
        #    self._dns_zone,
        #    self.stack_name,
        #    self.project_name,
        #    self.location,
        #    self._resource_group,
        # )
        # self._blob_container = BlobContainer(
        #     self._function_storage_account, self.stack_name, self.project_name, self.location, self._resource_group
        # )
        # self._functions_package = FunctionsPackage(
        #     self._blob_container, self._function_storage_account, self.stack_name, self.project_name, self.location, self._resource_group
        # )
        self._app_insights = AppInsights(
            self.event.stack_name,
            self.event.project_name,
            self.event.location,
            None,
            None,
            self._resource_group,
        )

        self._container_registry = ContainerRegistry(
            self.event.stack_name,
            self.event.project_name,
            self.event.location,
            None,
            None,
            self._resource_group,
        )

    async def retrieve_container_registry_credentials(self) -> Dict[str, str]:
        """
        Retrieves the container registry credentials.
        :return: A dictionary with the credentials.
        :rtype: Dict[str, str]
        """
        username = self.outcome.outputs.get(
            Outputs.CONTAINER_REGISTRY_USERNAME.value, None
        )
        if username is not None:
            username = username.value
        password = self.outcome.outputs.get(
            Outputs.CONTAINER_REGISTRY_PASSWORD.value, None
        )
        if password is not None:
            password = password.value
        url = self.outcome.outputs.get(Outputs.CONTAINER_REGISTRY_URL.value, None)
        if url is not None:
            url = url.value

        return {
            "credential_name": username,
            "credential_password": password,
            "docker_registry_url": url,
        }


# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
