"""Initial

Revision ID: 092e8ff77823
Revises: 
Create Date: 2022-06-16 00:07:28.145185

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '092e8ff77823'
down_revision = None
branch_labels = None
depends_on = None


ShopUnitTypeEnum = postgresql.ENUM('CATEGORY', 'OFFER', name='shop_unit_type_enum', create_type=False)


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    ShopUnitTypeEnum.create(bind=op.get_bind())
    op.create_table('shop_unit',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('type', ShopUnitTypeEnum, nullable=False),
    sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('parent_type', ShopUnitTypeEnum, nullable=True),
    sa.CheckConstraint("parent_id IS NULL AND parent_type IS NULL OR parent_id IS NOT NULL AND parent_type = 'CATEGORY'", name=op.f('ck_shop_unit_parent_type_validation')),
    sa.ForeignKeyConstraint(['parent_id', 'parent_type'], ['shop_unit.id', 'shop_unit.type'], name=op.f('fk_shop_unit_parent_id_shop_unit'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_shop_unit')),
    sa.UniqueConstraint('id', 'type', name=op.f('uq_shop_unit_id'))
    )
    op.create_table('shop_unit_import',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('type', ShopUnitTypeEnum, nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.CheckConstraint("type = 'CATEGORY' AND price IS NULL OR type = 'OFFER' AND price IS NOT NULL", name=op.f('ck_shop_unit_import_price_validation')),
    sa.ForeignKeyConstraint(['id', 'type'], ['shop_unit.id', 'shop_unit.type'], name=op.f('fk_shop_unit_import_id_shop_unit'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['parent_id'], ['shop_unit.id'], name=op.f('fk_shop_unit_import_parent_id_shop_unit'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', 'date', name=op.f('pk_shop_unit_import'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('shop_unit_import')
    op.drop_table('shop_unit')
    ShopUnitTypeEnum.drop(bind=op.get_bind())
    # ### end Alembic commands ###