from fastapi import APIRouter, Depends, Response, Request

from app.api.dependencies import get_auth_service, get_token_service

from app.logger import logger
from app.schemas import TokensResponse
from app.services.auth_service import AuthService

from app.services.token_service import TokenService

from app.utils.oauth import oauth

oauth_router = APIRouter(prefix="/oauth", tags=["OAuth"])


@oauth_router.get("/{provider}/login")
async def oauth_login(provider: str, request: Request):
    client = oauth.create_client(provider)
    if not client:
        return {"error": "Unsupported provider"}

    redirect_uri = request.url_for("oauth_callback", provider=provider)
    return await client.authorize_redirect(request, redirect_uri)


# Callback после успешного входа
@oauth_router.get("/{provider}/callback")
async def oauth_callback(provider: str, request: Request, response: Response,
                         auth_service: AuthService = Depends(get_auth_service),
                         token_service: TokenService = Depends(get_token_service)):
    client = oauth.create_client(provider)
    if not client:
        return {"error": "Unsupported provider"}

    token = await client.authorize_access_token(request)

    userinfo = await client.userinfo(token=token)
    logger.info(f"OAuth userinfo entered: {userinfo}")

    user = await auth_service.login_or_register_oauth_user(provider, userinfo)
    access, refresh = await token_service.generate_tokens_cookies(user.id, response)

    return TokensResponse(access_token=access, refresh_token=refresh,
                          message="You have successfully entered your account")
