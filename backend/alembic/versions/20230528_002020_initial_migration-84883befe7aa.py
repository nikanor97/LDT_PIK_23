"""initial_migration

Revision ID: 84883befe7aa
Revises: 
Create Date: 2023-05-28 00:20:20.580200

"""
from alembic import op
import sqlmodel
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '84883befe7aa'
down_revision = None
branch_labels = None
depends_on = None


def upgrade(engine_name: str) -> None:
    try:
        globals()["upgrade_%s" % engine_name]()
    except KeyError:
        pass


def downgrade(engine_name: str) -> None:
    try:
        globals()["downgrade_%s" % engine_name]()
    except KeyError:
        pass





def upgrade_users() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_name'), 'users', ['name'], unique=False)
    op.create_table('user_passwords',
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('hashed_password', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('user_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_passwords_user_id'), 'user_passwords', ['user_id'], unique=False)
    op.create_table('user_tokens',
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('access_token', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('refresh_token', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('token_type', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('access_expires_at', sa.DateTime(), nullable=False),
    sa.Column('refresh_expires_at', sa.DateTime(), nullable=False),
    sa.Column('user_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('is_valid', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_tokens_user_id'), 'user_tokens', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade_users() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_tokens_user_id'), table_name='user_tokens')
    op.drop_table('user_tokens')
    op.drop_index(op.f('ix_user_passwords_user_id'), table_name='user_passwords')
    op.drop_table('user_passwords')
    op.drop_index(op.f('ix_users_name'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###


def upgrade_projects() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('fittings',
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('groupname', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('image_b64', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('projects',
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('status', sa.Enum('created', 'in_progress', 'error', name='projectstatusoption'), nullable=True),
    sa.Column('type', sa.Enum('dxf', 'manual', name='projecttypeoption'), nullable=True),
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('bathroom_type', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_name'), 'projects', ['name'], unique=False)
    op.create_table('devices',
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('project_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('coord_x', sa.Numeric(), nullable=True),
    sa.Column('coord_y', sa.Numeric(), nullable=True),
    sa.Column('coord_z', sa.Numeric(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('dxf_files',
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('project_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('source_url', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_roles',
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('role_type', sa.Enum('author', 'view_only', 'worker', name='roletypeoption'), nullable=False),
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('user_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('project_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_project_role', 'user_roles', ['user_id', 'project_id', 'role_type'], unique=True)
    op.create_index(op.f('ix_user_roles_project_id'), 'user_roles', ['project_id'], unique=False)
    op.create_index(op.f('ix_user_roles_user_id'), 'user_roles', ['user_id'], unique=False)
    op.create_table('project_fittings',
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('project_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('fitting_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.ForeignKeyConstraint(['fitting_id'], ['fittings.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('project_id', 'fitting_id', name='project_fitting_constr')
    )
    op.create_index(op.f('ix_project_fittings_fitting_id'), 'project_fittings', ['fitting_id'], unique=False)
    op.create_index(op.f('ix_project_fittings_project_id'), 'project_fittings', ['project_id'], unique=False)
    # ### end Alembic commands ###


def downgrade_projects() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_roles_user_id'), table_name='user_roles')
    op.drop_index(op.f('ix_user_roles_project_id'), table_name='user_roles')
    op.drop_index('idx_user_project_role', table_name='user_roles')
    op.drop_table('user_roles')
    op.drop_table('dxf_files')
    op.drop_table('devices')
    op.drop_index(op.f('ix_projects_name'), table_name='projects')
    op.drop_table('projects')
    op.drop_table('fittings')
    op.drop_index(op.f('ix_project_fittings_project_id'), table_name='project_fittings')
    op.drop_index(op.f('ix_project_fittings_fitting_id'), table_name='project_fittings')
    op.drop_table('project_fittings')
    # ### end Alembic commands ###
    op.execute("""DROP TYPE projectstatusoption""")
    op.execute("""DROP TYPE roletypeoption""")
    op.execute("""DROP TYPE projecttypeoption""")
