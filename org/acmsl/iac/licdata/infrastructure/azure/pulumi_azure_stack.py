# vim: set fileencoding=utf-8
"""
org/acmsl/iac/licdata/infrastructure/azure/pulumi_azure_stack.py

This script defines the PulumiAzureStack class.

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
from org.acmsl.iac.licdata.infrastructure import PulumiStack
from pulumi import Output
from pythoneda.shared import Event, EventEmitter
from pythoneda.shared.artifact.events import (
    DockerImageAvailable,
    DockerImagePushed,
    DockerImagePushRequested,
    DockerImageRequested,
)
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
    PublicIpAddress,
    ResourceGroup,
    WebApp,
)
from typing import Dict


class PulumiAzureStack(PulumiStack):
    """
    Azure-specific Pulumi implementation of Licdata infrastructure stacks.

    Class name: PulumiAzureStack

    Responsibilities:
        - Use Azure-specific Pulumi stack as Licdata infrastructure stack.

    Collaborators:
        - org.acmsl.licdata.infrastructure.PulumiStack
    """

    def __init__(self, name: str, projectName: str, location: str):
        """
        Creates a new PulumiAzureStack instance.
        :param name: The name of the stack.
        :type name: str
        :param projectName: The name of the project.
        :type projectName: str
        :param location: The Azure location.
        :type location: str
        """
        super().__init__(name, projectName, location)
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
        self._docker_pull_role_definition = None
        self._docker_pull_role_assignment = None
        self._web_app = None

    @classmethod
    def instantiate(cls):
        """
        Creates an instance.
        :return: The new instance.
        :rtype: pythoneda.iac.pulumi.azure.PulumiAzureStackFactory
        """
        raise InvalidOperationError("Cannot instantiate PulumiAzureStack directly")

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
    def web_app(self) -> WebApp:
        """
        Retrieves the Azure WebApp.
        :return: Such WebApp.
        :rtype: pythoneda.iac.pulumi.azure.WebApp
        """
        return self._web_app

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

    @property
    def docker_pull_role_definition(self) -> DockerPullRoleDefinition:
        """
        Retrieves the Role Definition allowing the functions to perform Docker pulls.
        :return: Such instance.
        :rtype: pythoneda.iac.pulumi.azure.DorkecPullRoleDefinition
        """
        return self._docker_pull_role_definition

    @property
    def docker_pull_role_assignment(self) -> DockerPullRoleAssignment:
        """
        Retrieves the Role Assignment allowing the functions to perform Docker pulls.
        :return: Such instance.
        :rtype: pythoneda.iac.pulumi.azure.DockerPullRoleAssignment
        """
        return self._docker_pull_role_assignment

    def declare_infrastructure(self):
        """
        Creates the infrastructure.
        """
        self._resource_group = ResourceGroup(
            self.stack_name, self.project_name, self.location
        )
        self._resource_group.create()

        self._function_storage_account = FunctionStorageAccount(
            self.stack_name, self.project_name, self.location, self._resource_group
        )
        self._function_storage_account.create()

        self._app_service_plan = AppServicePlan(
            self.stack_name,
            self.project_name,
            self.location,
            None,
            None,
            None,
            None,
            None,
            self._resource_group,
        )
        self._app_service_plan.create()

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
            self.stack_name,
            self.project_name,
            self.location,
            None,
            None,
            self._resource_group,
        )
        self._app_insights.create()

        self._container_registry = ContainerRegistry(
            self.stack_name,
            self.project_name,
            self.location,
            None,
            None,
            self._resource_group,
        )
        self._container_registry.create()

    async def retrieve_container_registry_credentials(self) -> Dict[str, str]:
        """
        Retrieves the container registry credentials.
        :return: A dictionary with the credentials.
        :rtype: Dict[str, str]
        """
        print(self.outcome.outputs)
        username = self.outcome.outputs.get("container_registry_username", None)
        if username is not None:
            username = username.value
        password = self.outcome.outputs.get("container_registry_password", None)
        if password is not None:
            password = password.value
        url = self.outcome.outputs.get("container_registry_url", None)
        if url is not None:
            url = url.value

        return {
            "username": username,
            "password": password,
            "docker_registry_url": url,
        }

    def request_docker_image(self):
        """
        Emits a request for the Docker image.
        """
        return DockerImageRequested(
            "licdata",
            "latest",
            {
                "variant": "azure",
                "python_version": "3.11",
                "azure_base_image_version": "4",
            },
        )

    def declare_docker_resources(
        self,
        imageName: str,
        imageVersion: str,
        imageUrl: str = None,
    ):
        """
        Declares the Docker-dependent infrastructure resources.
        :param imageName: The name of the Docker image.
        :type imageName: str
        :param imageVersion: The version of the Docker image.
        :type imageVersion: str
        :param imageUrl: The url of the Docker image.
        :type imageUrl: str
        :return: Either a DockerResourcesUpdated or DockerResourcesUpdateFailed event.
        :rtype: pythoneda.shared.iac.events.DockerResourcesUpdated
        """
        result = self.declare_infrastructure()

        login_server = self.container_registry.login_server.apply(lambda name: name)

        self._web_app = WebApp(
            self.stack_name,
            self.project_name,
            self.location,
            imageName,
            imageVersion,
            login_server,
            None,
            self._app_insights,
            self._function_storage_account,
            self._app_service_plan,
            self._container_registry,
            self._resource_group,
        )
        self._web_app.create()

        self._docker_pull_role_definition = DockerPullRoleDefinition(
            self.stack_name,
            self.project_name,
            self.location,
            self._container_registry,
            self._resource_group,
        )
        self._docker_pull_role_definition.create()

        self._docker_pull_role_assignment = DockerPullRoleAssignment(
            self.stack_name,
            self.project_name,
            self.location,
            self._web_app,
            self._docker_pull_role_definition,
            self._container_registry,
            self._resource_group,
        )
        self._docker_pull_role_assignment.create()

    async def push_docker_image(self, event: DockerImagePushRequested) -> Event:
        """
        Pushes the Docker image to the container registry.
        :param event: The event requesting pushing a Docker image.
        :type event: pythoneda.shared.artifact.events.DockerImagePushRequested
        :return: An event representing the image has been pushed successfully or not.
        :rtype: Event
        """
        # Retrieve the registry credentials
        credentials = Output.all(
            self.resource_group.name, self.container_registry.name
        ).apply(
            lambda args: containerRegistry.list_registry_credentials(
                resource_group_name=args[0], registry_name=args[1]
            )
        )

        # Extract the username and password
        admin_username = credentials.apply(lambda c: c.username)
        admin_password = credentials.apply(lambda c: c.passwords[0].value)

        return DockerImagePushed(
            event.image_name,
            event.image_version,
            event.image_url,
            event.registry_url,
            event.metadata,
        )


# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
