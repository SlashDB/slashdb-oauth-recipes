# Google

## Config

The scripts take the necessary IDs and secrets from `config.ini`.

An example config is included.

Copy it:

```sh
cp config.example.ini config.ini
```

And replace the contents with your values.

- `service_account_info_file`: Path to the private key file for the Service Account.
    It's available for download when creating a key for the Service Account.
- `client_id`: ID of the Google OAuth2 Client
- `client_secret`: Secret of the Google OAuth2 Client
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
      google:
        idp_name: Google
        enabled: True
        claim_attribute: email
        user_config_attribute: email
        client_id: {CLIENT_ID}
        redirect_uri: http://slashdb.internal/login/callback?idp_id=google
        response_type: id_token
        scope: openid email
        jwks_uri: https://www.googleapis.com/oauth2/v3/certs
        authorization_endpoint: https://accounts.google.com/o/oauth2/v2/auth
        token_endpoint: https://oauth2.googleapis.com/token
        gui:
          visible: True
```

## Service Account

The `jwt_login_google_service_account.py` script showcases a 
Service Account authentication with SlashDB.

It uses the private key from `service_account_info_file` to authenticate with
Google and obtain an ID token and then uses that token to authenticate with
SlashDB.


### Required Setup

The Service Account needs to have the permissions to create an ID token for the script to work.

See this Google documentation for more information:
[https://cloud.google.com/iam/docs/create-short-lived-credentials-direct#sa-credentials-oidc]

A `configure_account.py` script is included, which adds the role to the Service Account,
but it requires the Service Account to have permissions to modify the IAM policy.


## Interactive

The `jwt_login_google_interactive.py` script showcases an
user account authentication with SlashDB.

It will open a browser tab in which the user will be asked to log in.
Once the user logs in, the script will use the acquired ID token to authenticate with SlashDB.
The token will also be saved in the cache file, so that the user will not have to log in next time.

Note: this flow requires a redirect uri for `http://127.0.0.1:5000/callback`.
