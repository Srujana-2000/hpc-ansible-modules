# HPE HPC module Collection for Ansible

## Requirements

- Ansible 2.9 or later
- Python 3.6 or later

## Installation

Install the HPE HPC ansible modules collection on your Ansible management host.

```
ansible-galaxy collection install hpe.hpc
```

## Available Modules

- hpc_get_system_fw_inv - Fetches the inventory information of the servers
- hpc_get_power_state - Helps to get power state of CrayXD 670
- hpc_update_system_firmware - This modules helps in the firmware update

## Support

HPE HPC ansible module Collection for Ansible is supported by HPE when used with HPE Cray servers. Please send an email to [srujana.yasa@hpe.com]to get started with any issue you might need assistance with. Engage with your HPE representative.

## Releasing, Versioning and Deprecation

This collection follows [Semantic Versioning](https://semver.org/). More details on versioning can be found [in the Ansible docs](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html#collection-versions).

We plan to regularly release new minor or bugfix versions once new features or bugfixes have been implemented.

Releasing the current major version happens from the `main` branch.

## License

HPE HPC modules Collection for Ansible is released under the GPL-3.0 license.

    Copyright (C) 2024  Hewlett Packard Enterprise Development LP

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

See https://github.com/Srujana-2000/hpc-ansible-modules/blob/main/LICENSCE for the full terms.

The modules interfacing with the array SDKs are released under the Apache-2.0 license.

    Copyright 2020 Hewlett Packard Enterprise Development LP

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

See [MODULE-LICENSE](https://github.com/hpe-storage/nimble-ansible-modules/blob/master/MODULE-LICENSE) for the full terms.

## Code of Conduct

This repository adheres to the [Ansible Community code of conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)
