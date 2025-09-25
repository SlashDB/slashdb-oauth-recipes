# Entra ID (formerly Azure AD)

## Config

The scripts take the necessary IDs and secrets from `config.ini`.

An example config is included.

Copy it:

```sh
cp config.example.ini config.ini
```

And replace the contents with your values.

- `tenant_id`: ID of the tenant within which you want to authenticate
- `client_id`: ID of the App registration within Entra ID
- `client_secret`: Secret value from the client secret in the App registration
    Only needed for the Service Principal authentication.
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
      entra-id:
        idp_name: Entra ID
        enabled: True
        claim_attribute: sub # The `sub` claim contains the Object ID of the Service Principal
        user_config_attribute: name
        client_id: {CLIENT_ID} # This doesn't need to be the same client, but must be within the same tenant
        redirect_uri: http://slashdb.internal/login/callback?idp_id=entra-id
        response_type: code
        scope: openid email
        jwks_uri: https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys
        authorization_endpoint: https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize
        token_endpoint: https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token
        gui:
          visible: True
```

## Service Principal

The `jwt_login_entra_id_service_principal.py` script showcases a 
Service Principal authentication with SlashDB.

It uses the Client ID and Client Secret to obtain an ID token from Entra ID
and then uses that token to authenticate with SlashDB.

## Interactive

The `jwt_login_entra_id_interactive.py` script showcases an
user account authentication with SlashDB.

It will open a browser tab in which the user will be asked to log in.
Once the user logs in, the script will use the acquired ID token to authenticate with SlashDB.
The token will also be saved in the cache file, so that the user will not have to log in next time.

Note: this flow requires a "Mobile and desktop applications" redirect uri for `http://localhost`.
