sqlite_database = "sqlite+aiosqlite:///auth.db"

secret_key = "secret_key"

allow_user_registration = True

min_build_version = "1.1.5"

token_lifetime = 3600

webhook_port = 443
webhook_ssl_cert = "/etc/letsencrypt/live/lotw-auth.clava.space/fullchain.pem"
webhook_ssl_priv = "/etc/letsencrypt/live/lotw-auth.clava.space/privkey.pem"
