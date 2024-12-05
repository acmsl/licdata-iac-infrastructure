# vim: set fileencoding=utf-8
"""
org/acmsl/iac/licdata/infrastructure/pulumi_stack.py

This script defines the PulumiStack class.

Copyright (C) 2024-today acmsl's Licdata IaC

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
import abc
from pulumi import automation as auto
from pulumi.automation.errors import CommandError
from pythoneda.shared import Event
from pythoneda.shared.artifact.events import DockerImageAvailable, DockerImageRequested
from pythoneda.shared.iac import Stack
from pythoneda.shared.iac.events import (
    InfrastructureUpdateFailed,
    InfrastructureUpdated,
)
from typing import List


class PulumiStack(Stack, abc.ABC):
    """
    Pulumi implementation of Licdata infrastructure stacks.

    Class name: PulumiStack

    Responsibilities:
        - Use Pulumi stack as Licdata infrastructure stack.

    Collaborators:
        - org.acmsl.licdata.domain.Stack
    """

    def __init__(self, stackName: str, projectName: str, location: str):
        """
        Creates a new PulumiStack instance.
        :param stackName: The name of the stack.
        :type stackName: str
        :param projectName: The name of the project.
        :type projectName: str
        :param location: The Azure location.
        :type location: str
        """
        super().__init__(stackName, projectName, location)

    async def up(self):
        """
        Brings up the stack.
        :return: Either an InfrastructureUpdated event or an InfrastructureUpdateFailed.
        :rtype: pythoneda.shared.iac.events.InfrastructureUpdated
        """

        def declare_infrastructure_wrapper():
            return self.declare_infrastructure()

        result = []

        stack = auto.create_or_select_stack(
            stack_name=self.stack_name,
            project_name=self.project_name,
            program=declare_infrastructure_wrapper,
        )

        # stack.workspace.install_plugin("azure-native", "v2.11.0")
        stack.set_config("azure-native:location", auto.ConfigValue(value=self.location))
        stack.refresh(on_output=self.__class__.logger().debug)

        try:
            outcome = stack.up(on_output=self.__class__.logger().debug)
            import json

            self.__class__.logger().info(
                f"update summary: \n{json.dumps(outcome.summary.resource_changes, indent=4)}"
            )
            result.append(
                InfrastructureUpdated(self.stack_name, self.project_name, self.location)
            )
            result.append(self.request_docker_image())
        except CommandError as e:
            self.__class__.logger().error(f"CommandError: {e}")
            result.append(
                InfrastructureUpdateFailed(
                    self.stack_name, self.project_name, self.location
                )
            )

        return result

    @abc.abstractmethod
    def declare_infrastructure(self):
        """
        Declares the infrastructure.
        """
        pass

    async def up_docker_resources(
        self, imageName: str, imageVersion: str, imageUrl: str
    ) -> List[Event]:
        """
        Brings up the Docker resources.
        :param imageName: The name of the Docker image.
        :type imageName: str
        :param imageVersion: The version of the Docker image.
        :type imageVersion: str
        :param imageUrl: The url of the Docker image.
        :type imageUrl: str
        :return: The list of resulting events.
        :rtype: List[Event]
        """

        def declare_docker_resources_wrapper():
            return self.declare_docker_resources(imageName, imageVersion, imageUrl)

        result = []

        stack = auto.create_or_select_stack(
            stack_name=self.stack_name,
            project_name=self.project_name,
            program=declare_docker_resources_wrapper,
        )

        # stack.workspace.install_plugin("azure-native", "v2.11.0")
        stack.set_config("azure-native:location", auto.ConfigValue(value=self.location))
        stack.refresh(on_output=self.__class__.logger().debug)

        try:
            outcome = stack.up(on_output=self.__class__.logger().debug)
            import json

            self.__class__.logger().info(
                f"update summary: \n{json.dumps(outcome.summary.resource_changes, indent=4)}"
            )
            result.append(
                InfrastructureUpdated(self.stack_name, self.project_name, self.location)
            )
        except CommandError as e:
            self.__class__.logger().error(f"CommandError: {e}")
            result.append(
                InfrastructureUpdateFailed(
                    self.stack_name, self.project_name, self.location
                )
            )

        return result

    @abc.abstractmethod
    def declare_docker_resources(self, event: DockerImageAvailable) -> List[Event]:
        """
        Declares the Docker resources.
        :param event: The event.
        :type event: pythoneda.shared.artifact.events.DockerImageAvailable
        :return: The list of resulting events.
        :rtype: List[pythoneda.shared.Event]
        """
        pass

    async def down(self):
        """
        Brings down the stack.
        """
        raise NotImplementedError()


# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
