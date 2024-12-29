# vim: set fileencoding=utf-8
"""
org/acmsl/iac/licdata/infrastructure/remove_docker_resources_with_pulumi.py

This script defines the RemoveDockerResourcesWithPulumi class.

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
from pythoneda.shared.iac import RemoveDockerResources
from pythoneda.shared.iac.events import (
    DockerResourcesRemovalRequested,
    DockerResourcesRemovalFailed,
    DockerResourcesRemoved,
)
from typing import List


class RemoveDockerResourcesWithPulumi(RemoveDockerResources, abc.ABC):
    """
    Pulumi implementation to remove Docker resources in IaC stacks.

    Class name: RemoveDockerResourcesWithPulumi

    Responsibilities:
        - Remove Docker resources using Pulumi.

    Collaborators:
        - pythoneda.shared.iac.RemoveDockerResources
    """

    def __init__(self, event: DockerResourcesRemovalRequested):
        """
        Creates a new RemoveDockerResourcesWithPulumi instance.
        :param event: The event.
        :type event: pythoneda.shared.iac.events.DockerResourcesRemovalRequested
        """
        super().__init__(event)

    async def perform(self) -> List[Event]:
        """
        Brings down the stack.
        :return: Either a DockerResourcesRemoved or a DockerResourcesRemovalFailed.
        :rtype: pythoneda.shared.Event
        """
        result = None

        def do_nothing():
            pass

        # TODO: delete Docker images in container registries
        if True:
            result = DockerResourcesRemoved(
                self.event.stack_name,
                self.event.project_name,
                self.event.location,
                [self.event.id] + self.event.previous_event_ids,
            )
        else:
            result = DockerResourcesRemovalFailed(
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
