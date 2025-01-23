from sqlalchemy.orm import Mapped, relationship
from fastapi_users.db import (
    SQLAlchemyBaseUserTableUUID,
    SQLAlchemyBaseOAuthAccountTableUUID,
)
from ..core.database import Base

class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship(
        "OAuthAccount", lazy="joined"
    )
