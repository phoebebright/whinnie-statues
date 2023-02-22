#!/bin/bash

set -e 
set -o pipefail 

setup_ansible() {
    ansible-galaxy install -f -p roles -r requirements.yml 
    ansible-playbook playbook.yml 
} 


setup_django() {
    cd $(dirname $(dirname $0))
    if [ -e ./cli.sh ]; then
      ./cli.sh python manage.py check
      ./cli.sh python manage.py collectstatic --noinput
    fi
} 

setup_ansible 
setup_django 
