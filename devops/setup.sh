#!/bin/bash

set -e 
set -o pipefail

ansible-galaxy install -p roles --force -r ./requirements.yml
ansible-playbook ./playbook.yml
