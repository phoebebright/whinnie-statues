Adding new Client to Skorie Realm
=============

INSTALL CUSTOM VERSION - git+https://github.com/phoebebright/django-keycloak.git
that allows multiple clients: one for local dev and one for production

https://django-keycloak.readthedocs.io/en/latest/

- Install django-keycloak and follow instructions from docs
- migrate
- Create new client in Skorie realm - export skorieweb and import and update
- Copy secret from creentials tab
- in django admin, create realms - one has tag equistatue and one testclient, these match 2 clients created.  Then refresh openid and fresh certs from actions menu

In settings add:

    KEYCLOAK_USE_REALM = 'equistatue'

in in settings local:

    KEYCLOAK_USE_REALM = 'testclient'


Will now have to access development using ngrok:

    ./ngrok http 8000 --subdomain=whinie

    http://whinie.ngrok.io/

