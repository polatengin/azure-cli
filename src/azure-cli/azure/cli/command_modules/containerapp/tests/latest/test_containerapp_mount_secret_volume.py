# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import time

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, live_only, StorageAccountPreparer,
                               LogAnalyticsWorkspacePreparer)

from .utils import create_containerapp_env

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))
# flake8: noqa
# noqa
# pylint: skip-file


class ContainerAppMountSecretTest(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northcentralus")
    @LogAnalyticsWorkspacePreparer(location="eastus", get_shared_key=True)
    def test_container_app_mount_secret_e2e(self, resource_group, laworkspace_customer_id, laworkspace_shared_key):
        import requests

        env = self.create_random_name(prefix='env', length=24)
        app = self.create_random_name(prefix='app1', length=24)

        create_containerapp_env(self, env, resource_group, logs_workspace=laworkspace_customer_id, logs_workspace_shared_key=laworkspace_shared_key)

        self.cmd('containerapp env show -n {} -g {}'.format(env, resource_group), checks=[
            JMESPathCheck('name', env)            
        ])

        secretRef1 = "mysecret"
        secretValue1 = "secretvalue1"
        secretRef2 = "anothersecret"
        secretValue2 = "secretvalue2"

        self.cmd(f'az containerapp create -g {resource_group} --environment {env} -n {app} --secrets {secretRef1}={secretValue1} {secretRef2}={secretValue2} --secret-volume-mount "mnt/secrets"')        
        
        self.cmd('containerapp show -g {} -n {}'.format(resource_group, app), checks=[
            JMESPathCheck('properties.template.volumes[0].storageType', 'Secret'), 
            # --secret-volume-mount mounts all secrets, not specific secrets, therefore no secrets should be returned.
            JMESPathCheck('properties.template.volumes[0].secrets', None)
        ])