# vim: set fileencoding=utf-8
"""
org/acmsl/iac/licdata/infrastructure/azure/update_azure_docker_resources_with_pulumi.py

This script defines the UpdateAzureDockerResourcesWithPulumi class.

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
from .licdata_web_app import LicdataWebApp
from .update_azure_infrastructure_with_pulumi import UpdateAzureInfrastructureWithPulumi
from org.acmsl.iac.licdata.infrastructure import UpdateDockerResourcesWithPulumi
import pulumi
import pulumi_azure_native.resources as resources
import pulumi_azure_native.insights as insights
import pulumi_azure_native.containerregistry as acr
import pulumi_azure_native.storage as storage
import pulumi_azure_native.web as web
from pythoneda.shared import Event, EventEmitter
from pythoneda.shared.artifact.events import (
    DockerImageAvailable,
    DockerImagePushed,
    DockerImagePushRequested,
    DockerImageRequested,
)
from pythoneda.shared.iac.events import (
    InfrastructureUpdateRequested,
    DockerResourcesUpdateRequested,
)
from pythoneda.shared.iac.pulumi.azure import (
    AppInsights,
    AppServicePlan,
    ContainerRegistry,
    DockerPullRoleAssignment,
    DockerPullRoleDefinition,
    FunctionStorageAccount,
    ResourceGroup,
    WebApp,
)
from typing import Dict, List


class UpdateAzureDockerResourcesWithPulumi(UpdateDockerResourcesWithPulumi):
    """
    Updates Azure-specific Docker resources in IaC stacks with Pulumi.

    Class name: UpdateAzureDockerResourcesWithPulumi

    Responsibilities:
        - Use Pulumi to update Azure-specific Docker resources of IaC stacks.

    Collaborators:
        - org.acmsl.licdata.infrastructure.UpdateDockerResourcesWithPulumi
    """

    def __init__(self, event: DockerResourcesUpdateRequested):
        """
        Creates a new UpdateAzureDockerResourcesWithPulumi instance.
        :param event: The update request.
        :type event: pythoneda.shared.iac.events.DockerResourcesUpdateRequested
        """
        super().__init__(event)
        self._docker_pull_role_definition = None
        self._docker_pull_role_assignment = None
        self._web_app = None

    @classmethod
    def instantiate(cls):
        """
        Creates an instance.
        :return: The new instance.
        :rtype: pythoneda.iac.pulumi.azure.UpdateAzureDockerResourcesWithPulumiFactory
        """
        raise InvalidOperationError(
            "Cannot instantiate UpdateAzureDockerResourcesWithPulumi directly"
        )

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

    def request_docker_image(self, secretName: str, registryUrl: str):
        """
        Emits a request for the Docker image.
        :param secretName: The name of the secret.
        :type secretName: str
        :param registryUrl: The url of the registry.
        :type registryUrl: str
        :return: A DockerImageRequested event.
        :rtype: pythoneda.shared.artifact.events.DockerImageRequested
        """
        return DockerImageRequested(
            "licdata",
            "latest",
            {
                "variant": "azure",
                "python_version": "3.11",
                "azure_base_image_version": "4",
                "credential_name": secretName,
                "docker_registry_url": registryUrl,
            },
            [self.event.id] + self.event.previous_event_ids,
        )

    def declare_docker_resources(self) -> List[Event]:
        """
        Declares the Docker-dependent infrastructure resources.
        :return: Either a DockerResourcesUpdated or DockerResourcesUpdateFailed event.
        :rtype: List[Event]
        """
        UpdateAzureInfrastructureWithPulumi.logger().debug(
            "Creating remaining Azure resources (WebApp, DockerPullRoleDefinition, DockerPullRoleAssignment)"
        )

        resource_group = self.get_resource_group()
        app_insights = self.get_app_insights(resource_group.name)
        container_registry = self.get_container_registry(resource_group.name)
        function_storage_account = self.get_function_storage_account(
            resource_group.name
        )
        app_service_plan = self.get_app_service_plan(resource_group.name)

        login_server = self.update_azure_resources_with_pulumi.container_registry.login_server.apply(
            lambda name: name
        )

        self._web_app = WebApp(
            self.event.stack_name,
            self.event.project_name,
            self.event.location,
            self.event.image_name,
            self.event.image_version,
            login_server,
            None,
            app_insights,
            function_storage_account,
            app_service_plan,
            container_registry,
            resource_group,
        )
        self._web_app.create()

        UpdateAzureDockerResourcesWithPulumi.logger().debug(
            f"WebApp created: {self._web_app}"
        )

        self._docker_pull_role_definition = DockerPullRoleDefinition(
            self.event.stack_name,
            self.event.project_name,
            self.event.location,
            container_registry,
            resource_group,
        )
        self._docker_pull_role_definition.create()

        self._docker_pull_role_assignment = DockerPullRoleAssignment(
            self.event.stack_name,
            self.event.project_name,
            self.event.location,
            self._web_app,
            self._docker_pull_role_definition,
            container_registry,
            resource_group,
        )
        self._docker_pull_role_assignment.create()

    def get_resource_group(self) -> resources.AwaitableGetResourceGroupResult:
        """
        Retrieves the Resource Group.
        :return: Such instance.
        :rtype: pythoneda.iac.pulumi.azure.ResourceGroup
        """
        return resources.get_resource_group(
            resource_group_name=ResourceGroup.name_for(
                self.event.stack_name, self.event.project_name, self.event.location
            )
        )

    def get_app_insights(
        self, resourceGroupName: str
    ) -> insights.AwaitableGetComponentResult:
        """
        Retrieves an Application Insights instance.
        :param resourceGroupName: The resource group name.
        :type resourceGroupName: str
        :return: Such instance.
        :rtype: pulumi_azure_native.insights.AwaitableGetcomponentResult
        """
        return insights.get_component(
            resource_group_name=resourceGroupName, resource_name=resourceGroupName
        )

    def get_container_registry(
        self, resourceGroupName: str
    ) -> acr.AwaitableGetRegistryResult:
        """
        Retrieves a Container Registry instance.
        :param resourceGroupName: The resource group name.
        :type resourceGroupName: str
        :return: Such instance.
        :rtype: pulumi_azure_native.containerregistry.AwaitableGetRegistryResult
        """
        return acr.get_registry(
            resource_group_name=resourceGroupName,
            registry_name=ContainerRegistry.name_for(
                self.event.stack_name, self.event.project_name, self.event.location
            ),
        )

    def get_storage_account(
        self, resourceGroupName: str
    ) -> storage.AwaitableGetStorageAccountResult:
        """
        Retrieves a Storage Account instance.
        :param resourceGroupName: The resource group name.
        :type resourceGroupName: str
        :return: Such instance.
        :rtype: pulumi_azure_native.storage.AwaitableGetStorageAccountResult
        """
        return storage.get_storage_account(
            resource_group_name=resourceGroupName,
            account_name=FunctionStorageAccount.name_for(
                self.event.stack_name, self.event.project_name, self.event.location
            ),
        )

    def get_app_service_plan(
        self, resourceGroupName: str
    ) -> web.AwaitableGetAppServicePlanResult:
        """
        Retrieves an App Service Plan instance.
        :param resourceGroupName: The resource group name.
        :type resourceGroupName: str
        :return: Such instance.
        :rtype: pulumi_azure_native.web.AwaitableGetAppServicePlanResult
        """
        return web.get_app_service_plan(
            resource_group_name=resourceGroupName,
            name=AppServicePlan.name_for(
                self.event.stack_name, self.event.project_name, self.event.location
            ),
        )


# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
