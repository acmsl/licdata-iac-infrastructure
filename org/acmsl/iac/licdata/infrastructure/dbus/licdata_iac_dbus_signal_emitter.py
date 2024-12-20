# vim: set fileencoding=utf-8
"""
org/acmsl/iac/licdata/infrastructure/dbus/licdata_iac_dbus_signal_emitter.py

This file defines the LicdataIacDbusSignalEmitter class.

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
from dbus_next import BusType
from pythoneda.shared.artifact.events import DockerImageRequested
from pythoneda.shared.artifact.events.infrastructure.dbus import (
    DbusDockerImageRequested,
)
from pythoneda.shared.iac.events import InfrastructureUpdated
from pythoneda.shared.iac.events.infrastructure.dbus import DbusInfrastructureUpdated
from pythoneda.shared.infrastructure.dbus import DbusSignalEmitter
from pythoneda.shared.runtime.secrets.events import CredentialIssued
from pythoneda.shared.runtime.secrets.events.infrastructure.dbus import (
    DbusCredentialIssued,
)
from typing import Dict


class LicdataIacDbusSignalEmitter(DbusSignalEmitter):
    """
    A Port that emits Licdata IaC's events as d-bus signals.

    Class name: LicdataIacDbusSignalEmitter

    Responsibilities:
        - Connect to d-bus.
        - Emit Licdata IaC's events as d-bus signals.

    Collaborators:
        - pythoneda.shared.application.PythonEDA: Requests emitting events.
        - pythoneda.shared.artifact.events.infrastructure.dbus.DbusDockerImageRequested
    """

    def __init__(self):
        """
        Creates a new LicdataIacDbusSignalEmitter instance.
        """
        super().__init__("org.acmsl.iac.licdata.events.infrastructure.dbus")

    def signal_emitters(self) -> Dict:
        """
        Retrieves the configured event emitters.
        :return: For each event, a list with the event interface and the bus type.
        :rtype: Dict
        """
        result = {}
        key = self.__class__.full_class_name(InfrastructureUpdated)
        result[key] = [DbusInfrastructureUpdated, BusType.SYSTEM]
        key = self.__class__.full_class_name(DockerImageRequested)
        result[key] = [DbusDockerImageRequested, BusType.SYSTEM]
        key = self.__class__.full_class_name(CredentialIssued)
        result[key] = [DbusCredentialIssued, BusType.SYSTEM]

        return result


# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
