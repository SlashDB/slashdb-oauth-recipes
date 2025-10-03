# Keycloak

## Config

The scripts take the necessary IDs and secrets from `config.ini`.

An example config is included.

Copy it:

```sh
cp config.example.ini config.ini
```

And replace the contents with your values.

For the secret values it's better to use environment variables instead of the text file.

- `keycloak_url`: URL to your Keycloak instance
    Env. variable name: `SLASHDB_KEYCLOAK_URL`
- `realm_name`: Name of your Keycloak realm
    Env. variable name: `SLASHDB_KEYCLOAK_REALM_NAME`
- `client_id`: ID of the Client within Keycloak
    Env. variable name: `SLASHDB_CLIENT_ID`
- `username`: Username of the Keycloak user
    Env. variable name: `SLASHDB_KEYCLOAK_USERNAME`
- `password`: Password of the Keycloak user
    Env. variable name: `SLASHDB_KEYCLOAK_PASSWORD`
- `slashdb_idp_id`: IDP ID assigned in `auth.cfg` of your SlashDB configuration
    Env. variable name: `SLASHDB_IDP_ID`
- `slashdb_url`: URL to your SlashDB instance
    Env. variable name: `SLASHDB_URL`

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

For the authentication to be successful, you need to have a matching user in SlashDB.
For example, the configuration above will match the user based on the email value,
so you need a user account in SlashDB with the email property matching the email of the user.

See the documentation for more information:
[https://docs.slashdb.com/user-guide/security/authentication/#sso-openid-connect]

## Script

The `jwt_login_keycloak.py` script showcases a Keycloak authentication with
SlashDB.

It uses the username and password to obtain an ID token from Keycloak
and then uses that token to authenticate with SlashDB.

Note: this uses a "Direct Access Grant" flow, which needs to be enabled in Keycloak
