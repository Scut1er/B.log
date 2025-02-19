TOKEN_ALGORITHM = "ES256"

ROLE_ADMIN = "admin"
ROLE_USER = "user"

OAUTH_PROVIDER_MAPPING = {
    "google": {"email": "email", "fullname": "name", "provider_id": "sub"},
    "yandex": {"email": "default_email", "fullname": "real_name", "provider_id": "id"}
}
