# vim: set fileencoding=utf-8
"""
org/acmsl/iac/licdata/infrastructure/update_docker_resources_with_pulumi.py

This script defines the UpdateDockerResourcesWithPulumi class.

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
from pythoneda.shared.iac import UpdateDockerResources
from pythoneda.shared.iac.events import (
    DockerResourcesUpdateRequested,
    DockerResourcesUpdateFailed,
    DockerResourcesUpdated,
)
from typing import List


class UpdateDockerResourcesWithPulumi(UpdateDockerResources, abc.ABC):
    """
    Updates Pulumi to update Docker resources of IaC stacks.

    Class name: UpdateDockerResourcesWithPulumi

    Responsibilities:
        - Updates Docker resources of IaC stacks using Pulumi.

    Collaborators:
        - pythoneda.shared.iac.UpdateDockerResources
    """

    def __init__(self, event: DockerResourcesUpdateRequested):
        """
        Creates a new UpdateDockerResourcesWithPulumi instance.
        :param event: The event.
        :type event: pythoneda.shared.iac.events.DockerResourcesUpdateRequested
        """
        super().__init__(event)

    @abc.abstractmethod
    def declare_docker_resources(self) -> Event:
        """
        Declares the Docker resources.
        :return: Either a DockerResourcesUpdated or a DockerResourcesUpdateFailed
        :rtype: Event
        """
        pass

    @abc.abstractmethod
    def declare_infrastructure(self) -> Event:
        """
        Declares the infrastructure resources.
        :return: Either a InfrastructureUpdated or a InfrastructureUpdateFailed
        :rtype: Event
        """
        pass

    async def perform(self) -> Event:
        """
        Brings up the Docker resources.
        :param event: The event.
        :type event: pythoneda.shared.iac.events.DockerResourcesUpdateRequested
        :return: Either a DockerResourcesUpdated or a DockerResourcesUpdateFailed
        :rtype: Event
        """

        def declare_docker_resources_wrapper():
            self.declare_infrastructure()
            return self.declare_docker_resources()

        result = None

        stack = auto.create_or_select_stack(
            stack_name=self.event.stack_name,
            project_name=self.event.project_name,
            program=declare_docker_resources_wrapper,
        )

        # stack.workspace.install_plugin("azure-native", "v2.11.0")
        stack.set_config(
            "azure-native:location", auto.ConfigValue(value=self.event.location)
        )
        stack.refresh(on_output=self.__class__.logger().debug)

        try:
            self._outcome = stack.up(on_output=self.__class__.logger().debug)
            import json

            self.__class__.logger().info(
                f"update summary: \n{json.dumps(self.outcome.summary.resource_changes, indent=4)}"
            )
            result = self._build_DockerResourcesUpdated_from_outcome(self._outcome)
        except CommandError as e:
            self.__class__.logger().error(f"CommandError: {e}")
            result = self._build_DockerResourcesUpdateFailed()

        return result

    @abc.abstractmethod
    def _build_DockerResourcesUpdated_from_outcome(
        self, outcome: auto.UpResult
    ) -> DockerResourcesUpdated:
        """
        Builds a DockerResourcesUpdated event from the outcome.
        :param outcome: The outcome.
        :type outcome: auto.UpResult
        :return: A DockerResourcesUpdated event.
        :rtype: pythoneda.shared.iac.events.DockerResourcesUpdated
        """
        pass

    def _build_DockerResourcesUpdateFailed(self) -> DockerResourcesUpdateFailed:
        """
        Builds a DockerResourcesUpdateFailed event.
        :return: A DockerResourcesUpdateFailed event.
        :rtype: pythoneda.shared.iac.events.DockerResourcesUpdateFailed
        """
        return DockerResourcesUpdateFailed(
            self.event.stack_name,
            self.event.project_name,
            self.event.location,
            self.event.metadata,
            [self.event.id] + self.event.previous_event_ids,
        )


# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
