# vim: set fileencoding=utf-8
"""
org/acmsl/iac/licdata/infrastructure/update_pulumi_stack.py

This script defines the UpdatePulumiStack class.

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
    DockerResourcesUpdateRequested,
    DockerResourcesUpdateFailed,
    InfrastructureUpdateFailed,
    InfrastructureUpdated,
)
from typing import List


class UpdatePulumiStack(Stack, abc.ABC):
    """
    Updates Pulumi-based Licdata infrastructure stacks.

    Class name: UpdatePulumiStack

    Responsibilities:
        - Updates Pulumi-based Licdata infrastructure stacks.

    Collaborators:
        - pythoneda.shared.iac.UpdateStack
    """

    def __init__(self, event: InfrastructureUpdateRequested):
        """
        Creates a new UpdatePulumiStack instance.
        :param event: The event.
        :type event: pythoneda.shared.iac.events.InfrastructureUpdateRequested
        """
        super().__init__(event)

    async def up(self, event: InfrastructureUpdateRequested):
        """
        Brings up the stack.
        :param event: The event.
        :type event: pythoneda.shared.iac.events.InfrastructureUpdateRequested
        :return: Either an InfrastructureUpdated event or an InfrastructureUpdateFailed.
        :rtype: pythoneda.shared.iac.events.InfrastructureUpdated
        """

        def declare_infrastructure_wrapper():
            return self.declare_infrastructure()

        result = []

        stack = auto.create_or_select_stack(
            stack_name=self.event.stack_name,
            project_name=self.event.project_name,
            program=declare_infrastructure_wrapper,
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
            event = InfrastructureUpdated(
                self.event.stack_name,
                self.event.project_name,
                self.event.location,
                [self.event.id] + self.event.previous_event_ids,
            )
            result.append(
                InfrastructureUpdated(
                    self.event.stack_name,
                    self.event.project_name,
                    self.event.location,
                    [self.event.id] + self.event.previous_event_ids,
                )
            )
        except CommandError as e:
            self.__class__.logger().error(f"CommandError: {e}")
            result.append(
                InfrastructureUpdateFailed(
                    self.event.stack_name,
                    self.event.project_name,
                    self.event.location,
                    [self.event.id] + self.event.previous_event_ids,
                )
            )

        return result

    @abc.abstractmethod
    def declare_infrastructure(self):
        """
        Declares the infrastructure.
        """
        pass

    async def up_docker_resources(self, event: DockerResourcesUpdateRequested) -> Event:
        """
        Brings up the Docker resources.
        :param event: The event.
        :type event: pythoneda.shared.iac.events.DockerResourcesUpdateRequested
        :return: Either a DockerResourcesUpdated or a DockerResourcesUpdateFailed
        :rtype: Event
        """

        def declare_docker_resources_wrapper():
            return self.declare_docker_resources(
                event.image_name,
                event.image_version,
                event.image_url,
                [event.id] + event.previous_event_ids,
            )

        result = None

        stack = auto.create_or_select_stack(
            stack_name=event.stack_name,
            project_name=event.project_name,
            program=declare_docker_resources_wrapper,
        )

        # stack.workspace.install_plugin("azure-native", "v2.11.0")
        stack.set_config(
            "azure-native:location", auto.ConfigValue(value=event.location)
        )
        stack.refresh(on_output=self.__class__.logger().debug)

        try:
            self._outcome = stack.up(on_output=self.__class__.logger().debug)
            import json

            self.__class__.logger().info(
                f"update summary: \n{json.dumps(self.outcome.summary.resource_changes, indent=4)}"
            )
            result = DockerResourcesUpdated(
                event.stack_name,
                event.project_name,
                event.location,
                [event.id] + event.previous_event_ids,
            )
        except CommandError as e:
            self.__class__.logger().error(f"CommandError: {e}")
            result = DockerResourcesUpdateFailed(
                event.stack_name,
                event.project_name,
                event.location,
                [event.id] + event.previous_event_ids,
            )

        return result


# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
