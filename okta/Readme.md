# Okta

## Config

The scripts take the necessary Okta user credentials from `config.ini`.

An example config is included.

Copy it:

```sh
cp config.example.ini config.ini
```

And replace the contents with your values.

For the secret values it's better to use environment variables instead of the text file.

| Attribute                                 | Description                                                 | Environment Variable          |
|-------------------------------------------|-------------------------------------------------------------|-------------------------------|
| `client_id` | Client ID assigned for Okta Native/Services App                               | `OKTA_CLIENT_ID`        |
| `client_secret` | Client Secret assigned for Okta Native/Services App                               | `OKTA_CLIENT_SECRET`        |
| `username`                              | Okta user username                                 | `OKTA_USERNAME` |
| `password`                               | Okta user password                            | `OKTA_PASSWORD`           |
| `slashdb_idp_id`                          | IDP ID assigned in `auth.cfg` of your SlashDB configuration | `SLASHDB_IDP_ID`              |
| `slashdb_url`                             | URL to your SlashDB instance                                | `SLASHDB_URL`                 |
| `token_url`                             | URL to your Okta token endpoint                                | `OKTA_TOKEN_URL`                 |

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
      okta:
        idp_name: Okta
        enabled: True
        claim_attribute: email
        user_config_attribute: email
        client_id: slashdb
        redirect_uri: http://slashdb.internal/login/callback?idp_id=okta
        response_type: code
        scope: openid email
        well_known_configuration: https://example.okta.com/.well-known/openid-configuration
        gui:
          visible: True
```

For the authentication to be successful, you need to have a matching user in SlashDB.
For example, the configuration above will match the user based on the email value,
so you need a user account in SlashDB with the email property matching the email of the user.

See the documentation for more information:
[https://docs.slashdb.com/user-guide/security/authentication/#sso-openid-connect]

## Script - User credentials

The `jwt_login_okta.py` script showcases an Okta authentication with
SlashDB using user credentials.

It uses the username and password to obtain an ID token from Okta
and then uses that token to authenticate with SlashDB.

Note: this uses an okta Native App and with Resource Owner Password enabled and with password only access policy in Okta Authentication Policies assigned to the Native App

## Script - Client Secret

The `jwt_service_okta.py` script showcases an Okta authentication with
SlashDB using the Okta application client secret.

It uses the Okta application client secret to obtain an ID token from Okta
and then uses that token to authenticate with SlashDB, this approach is recommended for Machine to Machine access (unattended jobs).
