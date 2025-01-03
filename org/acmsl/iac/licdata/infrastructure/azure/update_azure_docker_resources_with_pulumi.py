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
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
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
    Outputs,
    ResourceGroup,
    StorageAccount,
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
        self._docker_pull_role_definition = None
        self._docker_pull_role_assignment = None
        self._web_app = None
        self._update_azure_infrastructure_with_pulumi = (
            UpdateAzureInfrastructureWithPulumi(
                InfrastructureUpdateRequested(
                    event.stack_name,
                    event.project_name,
                    event.location,
                    event.metadata,
                    [event.id] + event.previous_event_ids,
                )
            )
        )
        super().__init__(event)

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

    def find_azure_resource_by_name_prefix(
        self, resourceGroupName: str, namePrefix: str, resourceType: str
    ) -> pulumi.Resource:
        """
        Finds an Azure resource by its name prefix.
        :param resourceGroupName: The name of the resource group.
        :type resourceGroupName: str
        :param namePrefix: The name prefix.
        :type namePrefix: str
        :param resourceType: The resource type.
        :type resourceType: str
        :return: The Azure resource.
        :rtype: pulumi.Resource
        """
        from azure.identity import DefaultAzureCredential
        from azure.mgmt.resource import ResourceManagementClient

        result = None

        credential = ClientSecretCredential(tenant_id, app_id, password)
        subscription_id = self.event.metadata.get("azure_subscription_id", None)
        resource_client = ResourceManagementClient(credential, subscription_id)

        print(
            f"Using ResourceManagementClient(ClientSecretCredential(tenant, app, password), subscription_id)"
        )

        try:
            resources = resource_client.resources.list_by_resource_group(
                resourceGroupName
            )

            filtered_resources = [
                res
                for res in resources
                if res.type.lower() == resource_type.lower()
                and res.name.startswith(namePrefix)
            ]

            if len(filtered_resources) > 0:
                result = filtered_resources[0]
        except Error as e:
            print(e)

        return result

    def declare_infrastructure(self) -> Event:
        """
        Declares the infrastructure resources.
        :return: Either a InfrastructureUpdated or a InfrastructureUpdateFailed
        :rtype: Event
        """
        return self._update_azure_infrastructure_with_pulumi.declare_infrastructure()

    def declare_docker_resources(self) -> List[Event]:
        """
        Declares the Docker-dependent infrastructure resources.
        :return: Either a DockerResourcesUpdated or DockerResourcesUpdateFailed event.
        :rtype: List[Event]
        """
        UpdateAzureDockerResourcesWithPulumi.logger().debug(
            "Creating remaining Azure resources (WebApp, DockerPullRoleDefinition, DockerPullRoleAssignment)"
        )

        self._web_app = WebApp(
            self.event.stack_name,
            self.event.project_name,
            self.event.location,
            self.event.image_name,
            self.event.image_version,
            self._update_azure_infrastructure_with_pulumi.container_registry.login_server.apply(
                lambda name: name
            ),
            None,
            self._update_azure_infrastructure_with_pulumi.app_insights,
            self._update_azure_infrastructure_with_pulumi.function_storage_account,
            self._update_azure_infrastructure_with_pulumi.app_service_plan,
            self._update_azure_infrastructure_with_pulumi.container_registry,
            self._update_azure_infrastructure_with_pulumi.resource_group,
        )
        self._docker_pull_role_definition = DockerPullRoleDefinition(
            self.event.stack_name,
            self.event.project_name,
            self.event.location,
            self._update_azure_infrastructure_with_pulumi.container_registry,
            self._update_azure_infrastructure_with_pulumi.resource_group,
        )
        self._docker_pull_role_assignment = DockerPullRoleAssignment(
            self.event.stack_name,
            self.event.project_name,
            self.event.location,
            self._web_app,
            self._docker_pull_role_definition,
            self._update_azure_infrastructure_with_pulumi.container_registry,
            self._update_azure_infrastructure_with_pulumi.resource_group,
        )


# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
