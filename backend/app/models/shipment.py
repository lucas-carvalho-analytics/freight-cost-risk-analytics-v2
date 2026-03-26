from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, Numeric, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[int] = mapped_column(primary_key=True)
    data_embarque: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    origem: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    destino: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    valor_carga: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    tipo_veiculo: Mapped[str] = mapped_column(String(80), nullable=False)
    transportadora: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    taxa_ad_valorem_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    frete_peso: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    ocorrencia: Mapped[str | None] = mapped_column(Text, nullable=True)
    tem_ocorrencia: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )
    ad_valorem: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
