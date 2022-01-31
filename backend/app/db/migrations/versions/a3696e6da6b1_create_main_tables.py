"""create_main_tables
Revision ID: a3696e6da6b1
Revises: 
Create Date: 2021-10-13 09:16:05.378958
"""
from alembic import op
import sqlalchemy as sa
from typing import Tuple
# revision identifiers, used by Alembic
revision = 'a3696e6da6b1'
down_revision = None
branch_labels = None
depends_on = None

def create_updated_at_trigger() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS
        $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """
    )
def timestamps(indexed: bool = False) -> Tuple[sa.Column, sa.Column]:
    return (
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=indexed,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=indexed,
        ),
    )
def create_users_table() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.Text, unique=True, nullable=False, index=True),
        sa.Column("email", sa.Text, unique=True, nullable=False, index=True),
        sa.Column("email_verified", sa.Boolean, nullable=False, server_default="False"),
        sa.Column("salt", sa.Text, nullable=False),
        sa.Column("super_salt", sa.Text, nullable=False),
        sa.Column("password", sa.Text, nullable=False),
        sa.Column("super_password", sa.Text, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="True"),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default="False"),
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_user_modtime
            BEFORE UPDATE
            ON users
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )
def create_profiles_table() -> None:
    op.create_table(
        "profiles",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("full_name", sa.Text, nullable=True),
        sa.Column("phone_number", sa.Text, nullable=True),
        sa.Column("bio", sa.Text, nullable=True, server_default=""),
        sa.Column("image", sa.Text, nullable=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")),
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_profiles_modtime
            BEFORE UPDATE
            ON profiles
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )
def create_cleanings_table() -> None:
    op.create_table(
        "cleanings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.Text, nullable=False, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("cleaning_type", sa.Text, nullable=False, server_default="spot_clean"),
        sa.Column("price", sa.Numeric(10, 5), nullable=False),
        sa.Column("owner", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")),
        *timestamps(indexed=True),
    )
    op.execute(
        """
        CREATE TRIGGER update_cleanings_modtime
            BEFORE UPDATE
            ON cleanings
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )
def create_courses_table() -> None:
    op.create_table(
        "courses",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.Text, nullable=False, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("link", sa.Text, nullable=True),
        sa.Column("price", sa.Numeric(10, 5), nullable=False),
        sa.Column("owner", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")),
        *timestamps(indexed=True),
    )
    op.execute(
        """
        CREATE TRIGGER update_courses_modtime
            BEFORE UPDATE
            ON courses
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )

def create_skills_table() -> None:
    op.create_table(
        "skills",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.Text,unique=True, nullable=False, index=True),
    )
    op.execute(
        """
        CREATE TRIGGER update_skills_modtime
            BEFORE UPDATE
            ON skills
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )

def create_skills_courses_table() -> None:
    op.create_table(
        "skills_courses",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("id_course", sa.Integer,sa.ForeignKey("courses.id", ondelete="CASCADE")),
        sa.Column("id_skill", sa.Integer,sa.ForeignKey("skills.id", ondelete="CASCADE"))
    )
    op.execute(
        """
        CREATE TRIGGER update_skills_modtime
            BEFORE UPDATE
            ON skills_courses
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )

def create_payments_table() -> None:
    op.create_table(
        "payments",
        sa.Column(
            "user_id",  # 'user' is a reserved word in postgres, so going with user_id instead
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "course_id",  # going with `cleaning_id` for consistency
            sa.Integer,
            sa.ForeignKey("courses.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("status", sa.Text, nullable=False, server_default="pending", index=True),
        *timestamps(),
    )
    op.create_primary_key("pk_payments", "payments", ["user_id", "course_id"])
    op.execute(
        """
        CREATE TRIGGER update_user_offers_for_cleanings_modtime
            BEFORE UPDATE
            ON payments
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )
def create_payments_table() -> None:
    op.create_table(
        "payments",
        sa.Column(
            "user_id",  # 'user' is a reserved word in postgres, so going with user_id instead
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "course_id",  # going with `cleaning_id` for consistency
            sa.Integer,
            sa.ForeignKey("courses.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("status", sa.Text, nullable=False, server_default="pending", index=True),
        *timestamps(),
    )
    op.create_primary_key("pk_payments", "payments", ["user_id", "course_id"])
    op.execute(
        """
        CREATE TRIGGER update_user_offers_for_cleanings_modtime
            BEFORE UPDATE
            ON payments
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )



def create_assessments_table() -> None:
    op.create_table(
        "assessments",
        sa.Column(
            "user_id",  # 'user' is a reserved word in postgres, so going with user_id instead
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "course_id",  # going with `cleaning_id` for consistency
            sa.Integer,
            sa.ForeignKey("courses.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("rating", sa.Integer, nullable=False,  index=True),
        *timestamps(),
    )
    op.create_primary_key("pk_assessments",'assessments', ["user_id", "course_id"])
    op.execute(
        """
        CREATE TRIGGER update_user_offers_for_cleanings_modtime
            BEFORE UPDATE
            ON assessments
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )

def create_password_groups_table() -> None:
    op.create_table(
        "password_groups",
        # sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer,sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("password_id", sa.Integer,sa.ForeignKey("passwords.id", ondelete="CASCADE"))
    )
    op.create_primary_key("pk_password_groups", "password_groups", ["user_id", "password_id"])
    op.execute(
        """
        CREATE TRIGGER update_password_groups_modtime
            BEFORE UPDATE
            ON password_groups
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )
def create_passwords_table() -> None:
    op.create_table(
        "passwords",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("description", sa.Text, nullable=True, index=True),
        sa.Column("password", sa.LargeBinary, nullable=False, index=True),
        sa.Column("iv", sa.LargeBinary, nullable=False, index=True),
        sa.Column("salt", sa.LargeBinary, nullable=False, index=True),

    )
    op.execute(
        """
        CREATE TRIGGER update_passwords_modtime
            BEFORE UPDATE
            ON passwords
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )


def upgrade() -> None:
    create_updated_at_trigger()
    create_users_table()
    create_profiles_table()
    # create_cleanings_table()
    create_courses_table()
    create_skills_table()
    create_skills_courses_table()
    create_payments_table()
    create_assessments_table()
    create_passwords_table()
    create_password_groups_table()

def downgrade() -> None:
    op.drop_table("assessments")
    op.drop_table("payments")
    # op.drop_table("cleanings")
    op.drop_table("skills_courses")
    op.drop_table('courses')
    op.drop_table("password_groups")
    op.drop_table("passwords")
    op.drop_table("profiles")
    op.drop_table("users")
    op.drop_table("skills")
    op.execute("DROP FUNCTION update_updated_at_column")
