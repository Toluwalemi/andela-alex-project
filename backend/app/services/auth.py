from functools import lru_cache

import jwt
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import User


class ClerkAuthService:
    def get_or_create_user(self, db: Session, token: str) -> User:
        claims = self.verify_token(token)
        clerk_user_id = claims.get("sub")
        if not clerk_user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject.")

        user = db.scalar(select(User).where(User.clerk_user_id == clerk_user_id))
        if user:
            user.email = claims.get("email") or user.email
            user.full_name = self._build_name(claims) or user.full_name
        else:
            user = User(
                clerk_user_id=clerk_user_id,
                email=claims.get("email"),
                full_name=self._build_name(claims),
            )
            db.add(user)

        db.commit()
        db.refresh(user)
        return user

    def verify_token(self, token: str) -> dict:
        try:
            signing_key = self._jwks_client().get_signing_key_from_jwt(token)
            return jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                issuer=settings.clerk_issuer,
                options={"verify_aud": False},
            )
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to verify Clerk token.",
            ) from exc

    @staticmethod
    def _build_name(claims: dict) -> str | None:
        first_name = claims.get("first_name")
        last_name = claims.get("last_name")
        full_name = " ".join(part for part in [first_name, last_name] if part)
        return full_name or claims.get("name")

    @staticmethod
    @lru_cache(maxsize=1)
    def _jwks_client() -> jwt.PyJWKClient:
        return jwt.PyJWKClient(settings.clerk_jwks_url)


clerk_auth_service = ClerkAuthService()

