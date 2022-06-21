from enum import Enum, unique

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.hybrid import hybrid_property

from .base import Base


@unique
class ShopUnitType(str, Enum):
    CATEGORY = 'CATEGORY'
    OFFER = 'OFFER'


ShopUnitTypeEnum = postgresql.ENUM(
    ShopUnitType, name='shop_unit_type_enum', create_type=False
)


class ShopUnit(Base):
    __tablename__ = 'shop_unit'

    id = sa.Column(postgresql.UUID(as_uuid=True), primary_key=True)
    type = sa.Column(ShopUnitTypeEnum, nullable=False)

    parent_id = sa.Column(postgresql.UUID(as_uuid=True))
    parent_type = sa.Column(ShopUnitTypeEnum)

    __table_args__ = (
        sa.UniqueConstraint(id, type),
        sa.ForeignKeyConstraint(
            [parent_id, parent_type], [id, type],
            ondelete='CASCADE', onupdate='CASCADE'
        ),
        sa.CheckConstraint(
            'parent_id IS NULL AND parent_type IS NULL '
            f'OR parent_id IS NOT NULL AND parent_type = \'{ShopUnitType.CATEGORY}\'',
            name='parent_type_validation'
        )
    )


class ShopUnitImport(Base):
    __tablename__ = 'shop_unit_import'

    id = sa.Column(postgresql.UUID(as_uuid=True), primary_key=True)
    type = sa.Column(ShopUnitTypeEnum, nullable=False)
    date = sa.Column(sa.DateTime, primary_key=True, nullable=False)
    parent_id = sa.Column(
        postgresql.UUID(as_uuid=True),
        sa.ForeignKey(ShopUnit.id, ondelete='SET NULL', onupdate='CASCADE')
    )
    name = sa.Column(sa.Text, nullable=False)
    price = sa.Column(sa.Integer)
    expiration_date = sa.Column(sa.DateTime)

    @hybrid_property
    def actuality_period(self):
        return sa.func.tsrange(self.date, self.expiration_date, '[)')

    __table_args__ = (
        sa.ForeignKeyConstraint(
            [id, type], [ShopUnit.id, ShopUnit.type],
            ondelete='CASCADE', onupdate='CASCADE'
        ),
        sa.CheckConstraint(
            f'type = \'{ShopUnitType.CATEGORY}\' AND price IS NULL '
            f'OR type = \'{ShopUnitType.OFFER}\' AND price IS NOT NULL',
            name='price_validation'
        ),
        sa.ForeignKeyConstraint(
            [id, expiration_date], [id, date],
            ondelete='SET NULL', onupdate='CASCADE'
        ),
        sa.UniqueConstraint(id, expiration_date),
        sa.CheckConstraint(
            'expiration_date IS NULL OR expiration_date > date',
            name='expiration_date_validation'
        )
    )
