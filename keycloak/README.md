# Keycloak

## Config

The scripts take the necessary IDs and secrets from `config.ini`.

An example config is included.

Copy it:

```sh
cp config.example.ini config.ini
```

And replace the contents with your values.

- `keycloak_url`: URL to your Keycloak instance
- `realm_name`: Name of your Keycloak realm
- `client_id`: ID of the Client within Keycloak
- `username`: Username of the Keycloak user
- `password`: Password of the Keycloak user
- `slashdb_idp_id`: IDP ID assigned in `auth.cfg` of your SlashDB configuration
- `slashdb_url`: URL to your SlashDB instance

## SlashDB Config

For the JWT authentication to work, you need to set up SlashDB properly.

In the `auth.cfg` file, add a new identity provider in the `jwt` section.
Here's an example:

```yaml
authentication_policies:
  jwt:
    enabled: True
    priority: 10
    gui:
      visible: True
    identity_providers:
      keycloak:
        idp_name: Keycloak
        enabled: True
        claim_attribute: email
        user_config_attribute: email
        client_id: slashdb
        redirect_uri: http://slashdb.internal/login/callback?idp_id=keycloak
        response_type: code
        scope: openid email
        well_known_configuration: http://keycloak.internal/realms/my-realm/.well-known/openid-configuration
        gui:
          visible: True
```

## Script

The `jwt_login_keycloak.py` script showcases a Keycloak authentication with
SlashDB.

It uses the username and password to obtain an ID token from Keycloak
and then uses that token to authenticate with SlashDB.

Note: this uses a "Direct Access Grant" flow, which needs to be enabled in Keycloak
