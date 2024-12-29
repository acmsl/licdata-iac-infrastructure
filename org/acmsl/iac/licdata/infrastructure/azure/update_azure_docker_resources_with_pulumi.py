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
from pulumi import Output
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
        self._update_azure_infrastructure_with_pulumi = (
            UpdateAzureInfrastructureWithPulumi(
                InfrastructureUpdateRequested(
                    event.stack_name,
                    event.project_name,
                    event.location,
                    [event.id] + event.previous_event_ids,
                )
            )
        )
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
    def update_azure_infrastructure_with_pulumi(
        self,
    ) -> UpdateAzureInfrastructureWithPulumi:
        """
        Retrieves the UpdateAzureInfrastructureWithPulumi instance.
        :return: Such instance.
        :rtype: org.acmsl.iac.licdata.infrastructure.azure.UpdateAzureInfrastructureWithPulumi
        """
        return self._update_azure_infrastructure_with_pulumi

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
        )

    def declare_docker_resources(
        self, event: DockerResourcesUpdateRequested
    ) -> List[Event]:
        """
        Declares the Docker-dependent infrastructure resources.
        :param event: The request.
        :type event: pythoneda.shared.iac.events.DockerResourcesUpdateRequested
        :return: Either a DockerResourcesUpdated or DockerResourcesUpdateFailed event.
        :rtype: List[Event]
        """
        result = self.update_azure_resources_with_pulumi.up()

        login_server = self.update_azure_resources_with_pulumi.container_registry.login_server.apply(
            lambda name: name
        )

        self._web_app = WebApp(
            event.stack_name,
            event.project_name,
            event.location,
            event.image_name,
            event.image_version,
            login_server,
            None,
            self.update_azure_resources_with_pulumi.app_insights,
            self.update_azure_resources_with_pulumi.function_storage_account,
            self.update_azure_resources_with_pulumi.app_service_plan,
            self.update_azure_resources_with_pulumi.container_registry,
            self.update_azure_resources_with_pulumi.resource_group,
        )
        self._web_app.create()

        self._docker_pull_role_definition = DockerPullRoleDefinition(
            event.stack_name,
            event.project_name,
            event.location,
            self.update_azure_resources_with_pulumi.container_registry,
            self.update_azure_resources_with_pulumi.resource_group,
        )
        self._docker_pull_role_definition.create()

        self._docker_pull_role_assignment = DockerPullRoleAssignment(
            event.stack_name,
            event.project_name,
            event.location,
            self._web_app,
            self._docker_pull_role_definition,
            self.update_azure_resources_with_pulumi.container_registry,
            self.update_azure_resources_with_pulumi.resource_group,
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
            [event.id] + event.previous_event_ids,
        )


# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
