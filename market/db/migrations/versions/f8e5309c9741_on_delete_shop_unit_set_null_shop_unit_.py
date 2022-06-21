"""On delete shop_unit set null shop_unit_import parent_id 

Revision ID: f8e5309c9741
Revises: aaa57a8173f0
Create Date: 2022-06-21 15:50:49.455217

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f8e5309c9741'
down_revision = 'aaa57a8173f0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_shop_unit_import_parent_id_shop_unit',
                       'shop_unit_import', type_='foreignkey')
    op.create_foreign_key(op.f('fk_shop_unit_import_parent_id_shop_unit'), 'shop_unit_import', 'shop_unit', 
                          ['parent_id'], ['id'], onupdate='CASCADE', ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('fk_shop_unit_import_parent_id_shop_unit'),
                       'shop_unit_import', type_='foreignkey')
    op.create_foreign_key('fk_shop_unit_import_parent_id_shop_unit', 'shop_unit_import', 'shop_unit', 
                          ['parent_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    # ### end Alembic commands ###