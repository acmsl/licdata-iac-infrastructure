# vim: set fileencoding=utf-8
"""
org/acmsl/iac/licdata/infrastructure/azure/pulumi_azure_stack_operation_factory.py

This script defines the PulumiAzureStackOperationFactory class.

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
from pythoneda.shared.artifact.events import DockerImageRequested
from pythoneda.shared.iac import (
    StackOperationFactory,
    RemoveDockerResources,
    RemoveInfrastructure,
    UpdateDockerResources,
    UpdateInfrastructure,
)
from pythoneda.shared.iac.events import (
    DockerImageDetailsRequested,
    DockerResourcesRemovalRequested,
    DockerResourcesUpdateRequested,
    InfrastructureRemovalRequested,
    InfrastructureUpdateRequested,
)
from typing import Dict, Union
from .request_azure_docker_image_details import RequestAzureDockerImageDetails
from .update_azure_docker_resources_with_pulumi import (
    UpdateAzureDockerResourcesWithPulumi,
)
from .update_azure_infrastructure_with_pulumi import UpdateAzureInfrastructureWithPulumi


class PulumiAzureStackOperationFactory(StackOperationFactory):
    """
    Creates Azure-specific Pulumi stacks.

    Class name: PulumiAzureStackOperationFactory

    Responsibilities:
        - Create PulumiAzureStack instances.

    Collaborators:
        - org.acmsl.licdata.infrastructure.azure.PulumiAzureStack
    """

    def __init__(self):
        """
        Creates a new PulumiAzureStackOperationFactory instance.
        """
        super().__init__()

    @classmethod
    def instantiate(cls):
        """
        Creates an instance.
        :return: The new instance.
        :rtype: org.acmsl.iac.licdata.infrastructure.azure.PulumiAzureStackOperationFactory
        """
        return cls()

    def new(
        self,
        event: Union[
            DockerImageDetailsRequested,
            DockerResourcesRemovalRequested,
            DockerResourcesUpdateRequested,
            InfrastructureRemovalRequested,
            InfrastructureUpdateRequested,
        ],
    ) -> Union[
        DockerImageRequested,
        RemoveDockerResources,
        RemoveInfrastructure,
        UpdateDockerResources,
        UpdateInfrastructure,
    ]:
        """
        Creates a new stack operation based on given event.
        :param event: The request.
        :type event: Union[DockerResourcesRemovalRequested, DockerResourcesUpdateRequested, InfrastructureRemovalRequested, InfrastructureUpdateRequested]
        :return: The stack operation, or None if the request is not supported.
        :rtype: Union[RemoveDockerResources, RemoveInfrastructure, UpdateDockerResources, UpdateInfrastructure],
        """
        result = None
        if isinstance(event, DockerImageDetailsRequested):
            result = RequestAzureDockerImageDetails(event)
        elif isinstance(event, DockerResourcesUpdateRequested):
            result = UpdateAzureDockerResourcesWithPulumi(event)
        elif isinstance(event, InfrastructureUpdateRequested):
            result = UpdateAzureInfrastructureWithPulumi(event)

        return result


# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
