# vim: set fileencoding=utf-8
"""
org/acmsl/iac/licdata/infrastructure/remove_pulumi_stack.py

This script defines the RemovePulumiStack class.

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
from pythoneda.shared.iac import RemoveStack
from pythoneda.shared.iac.events import (
    DockerResourcesRemovalRequested,
    DockerResourcesRemovalFailed,
    DockerResourcesRemoved,
    InfrastructureRemoved,
    InfrastructureRemovalFailed,
)
from typing import List


class RemovePulumiStack(RemoveStack, abc.ABC):
    """
    Pulumi implementation to remove Licdata infrastructure stacks.

    Class name: RemovePulumiStack

    Responsibilities:
        - Remove Pulumi-based Licdata infrastructure stacks.

    Collaborators:
        - pythoneda.shared.iac.RemoveStack
    """

    def __init__(self, event: InfrastructureRemovalRequested):
        """
        Creates a new RemovePulumiStack instance.
        :param event: The event.
        :type event: pythoneda.shared.iac.events.InfrastructureRemovalRequested
        """
        super().__init__(event)

    async def remove(self) -> List[Event]:
        """
        Brings down the stack.
        :return: Either an InfrastructureRemoved or an InfrastructureRemovalFailed.
        :rtype: pythoneda.shared.Event
        """
        result = None

        def do_nothing():
            pass

        stack = auto.create_or_select_stack(
            stack_name=self.event.stack_name,
            project_name=self.event.project_name,
            program=do_nothing,
        )

        stack.set_config(
            "azure-native:location", auto.ConfigValue(value=event.location)
        )
        stack.refresh(on_output=self.__class__.logger().debug)

        try:
            self._outcome = stack.destroy(on_output=self.__class__.logger().debug)
            import json

            self.__class__.logger().info(
                f"destroy summary: \n{json.dumps(self.outcome.summary.resource_changes, indent=4)}"
            )
            result = InfrastructureRemoved(
                self.event.stack_name,
                self.event.project_name,
                self.event.location,
                [self.event.id] + self.event.previous_event_ids,
            )
        except CommandError as e:
            self.__class__.logger().error(f"CommandError: {e}")
            result = InfrastructureRemovalFailed(
                self.event.stack_name,
                self.event.project_name,
                self.event.location,
                [self.event.id] + self.event.previous_event_ids,
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
