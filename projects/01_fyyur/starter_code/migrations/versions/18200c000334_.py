"""empty message

Revision ID: 18200c000334
Revises: 22c0f18dc638
Create Date: 2020-04-14 19:16:37.000435

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '18200c000334'
down_revision = '22c0f18dc638'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('VenueGenres')
    op.add_column('Venue', sa.Column('genres', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'genres')
    op.create_table('VenueGenres',
    sa.Column('genre_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('venue_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['genre_id'], ['Genre.id'], name='VenueGenres_genre_id_fkey'),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], name='VenueGenres_venue_id_fkey'),
    sa.PrimaryKeyConstraint('genre_id', 'venue_id', name='VenueGenres_pkey')
    )
    # ### end Alembic commands ###