# vim: set fileencoding=utf-8
"""
org/acmsl/iac/licdata/infrastructure/azure/request_azure_docker_image_details.py

This script defines the RequestAzureDockerImageDetails class.

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
from pythoneda.shared.iac import RequestDockerImageDetails
from pythoneda.shared.iac.events import DockerImageDetailsRequested


class RequestAzureDockerImageDetails(RequestDockerImageDetails):
    """
    Azure-specific Pulumi implementation of Licdata infrastructure stacks.

    Class name: RequestAzureDockerImageDetails

    Responsibilities:
        - Use Azure-specific Pulumi stack as Licdata infrastructure stack.

    Collaborators:
        - pythoneda.shared.iac.RequestDockerImageDetails
    """

    def __init__(self, event: DockerImageDetailsRequested):
        """
        Creates a new RequestAzureDockerImageDetails instance.
        :param event: The request.
        :type event: pythoneda.shared.iac.events.DockerImageDetailsRequested
        """
        super().__init__(event)

    @classmethod
    def instantiate(cls):
        """
        Creates an instance.
        :return: The new instance.
        :rtype: pythoneda.iac.pulumi.azure.RequestAzureDockerImageDetails
        """
        raise InvalidOperationError(
            "Cannot instantiate RequestAzureDockerImageDetails directly"
        )

    async def perform(self):
        """
        Emits a request for the Docker image.
        :return: A DockerImageRequested event.
        :rtype: pythoneda.shared.artifact.events.DockerImageRequested
        """
        return [
            DockerImageRequested(
                "licdata",
                "latest",
                {
                    "variant": "azure",
                    "python_version": "3.11",
                    "azure_base_image_version": "4",
                    "credential_name": self.event.metadata.get("credential_name", None),
                    "docker_registry_url": self.event.metadata.get(
                        "docker_registry_url", None
                    ),
                },
            )
        ]


# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
