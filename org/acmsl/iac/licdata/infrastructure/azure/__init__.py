# vim: set fileencoding=utf-8
"""
org/acmsl/iac/licdata/infrastructure/azure/__init__.py

This file ensures org.acmsl.iac.licdata.infrastructure.azure is a package.

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
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from .functions_deployment_slot import FunctionsDeploymentSlot
from .functions_package import FunctionsPackage
from .licdata_api import LicdataApi
from .licdata_web_app import LicdataWebApp
from .update_azure_docker_resources_with_pulumi import (
    UpdateAzureDockerResourcesWithPulumi,
)
from .update_azure_infrastructure_with_pulumi import UpdateAzureInfrastructureWithPulumi
from .pulumi_azure_stack_operation_factory import PulumiAzureStackOperationFactory

# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
