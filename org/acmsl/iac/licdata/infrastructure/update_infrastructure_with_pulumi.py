# vim: set fileencoding=utf-8
"""
org/acmsl/iac/licdata/infrastructure/update_infrastructure_with_pulumi.py

This script defines the UpdateInfrastructureWithPulumi class.

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
from pythoneda.shared.iac import UpdateInfrastructure
from pythoneda.shared.iac.events import (
    InfrastructureUpdateRequested,
    InfrastructureUpdateFailed,
    InfrastructureUpdated,
)
from typing import Dict, List


class UpdateInfrastructureWithPulumi(UpdateInfrastructure, abc.ABC):
    """
    Updates Pulumi to update infrastructure of IaC stacks.

    Class name: UpdateInfrastructureWithPulumi

    Responsibilities:
        - Updates infrastructure of IaC stacks using Pulumi.

    Collaborators:
        - pythoneda.shared.iac.UpdateInfrastructure
    """

    def __init__(self, event: InfrastructureUpdateRequested):
        """
        Creates a new UpdateInfrastructureWithPulumi instance.
        :param event: The event.
        :type event: pythoneda.shared.iac.events.InfrastructureUpdateRequested
        """
        super().__init__(event)

    async def perform(self):
        """
        Brings up the stack.
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
                self.event.metadata,
                [self.event.id] + self.event.previous_event_ids,
            )
            result.append(event)

        except CommandError as e:
            self.__class__.logger().error(f"CommandError: {e}")
            result.append(
                InfrastructureUpdateFailed(
                    self.event.stack_name,
                    self.event.project_name,
                    self.event.location,
                    self.event.metadata,
                    [self.event.id] + self.event.previous_event_ids,
                )
            )

        return result

    @abc.abstractmethod
    def declare_infrastructure(self, event: InfrastructureUpdateRequested):
        """
        Declares the infrastructure.
        :param event: The event.
        :type event: pythoneda.shared.iac.events.InfrastructureUpdateRequested
        """
        pass

    @abc.abstractmethod
    async def retrieve_container_registry_credentials(self) -> Dict[str, str]:
        """
        Retrieves the container registry credentials.
        :return: A dictionary with the credentials.
        :rtype: Dict[str, str]
        """
        pass


# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
