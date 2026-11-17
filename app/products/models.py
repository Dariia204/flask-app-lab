
from datetime import datetime
from sqlalchemy import Integer, String, Float, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db


class Category(db.Model):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(128), nullable=False, unique=True
    )

    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="category",
    )


class Product(db.Model):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    price: Mapped[float] = mapped_column(
        Float, nullable=False
    )

    category_id: Mapped[int | None] = mapped_column(
        db.ForeignKey("categories.id")
    )

    category: Mapped["Category | None"] = relationship(
        "Category",
        back_populates="products",
    )

    active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    def __repr__(self):
        return f"<Product {self.name} - ${self.price}>"
