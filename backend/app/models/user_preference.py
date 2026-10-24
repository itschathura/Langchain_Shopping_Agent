from sqlalchemy import Boolean, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    prefers_organic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    max_price_limit: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "prefers_organic": self.prefers_organic,
            "max_price_limit": float(self.max_price_limit) if self.max_price_limit is not None else None,
            "notes": self.notes,
        }

