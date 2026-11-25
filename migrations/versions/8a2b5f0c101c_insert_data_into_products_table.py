
"""Insert data into products table."""

from alembic import op
import sqlalchemy as sa


revision = '8a2b5f0c101c'
down_revision = 'e8e734153c80'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        INSERT INTO categories (name)
        VALUES ('Smartphones'), ('Accessories')
    """)

    op.execute("""
        INSERT INTO products
            (name, price, category_id, active)
        VALUES
            (
                'Samsung Galaxy S24',
                899.99,
                (SELECT id FROM categories
                 WHERE name = 'Smartphones'),
                TRUE
            ),
            (
                'Google Pixel 8',
                699.99,
                (SELECT id FROM categories
                 WHERE name = 'Smartphones'),
                TRUE
            ),
            (
                'Wireless Mouse',
                29.99,
                (SELECT id FROM categories
                 WHERE name = 'Accessories'),
                TRUE
            ),
            (
                'Keyboard',
                59.99,
                (SELECT id FROM categories
                 WHERE name = 'Accessories'),
                TRUE
            )
    """)


def downgrade():
    op.execute("""
        DELETE FROM products
        WHERE
            (name IN ('Samsung Galaxy S24', 'Google Pixel 8')
             AND category_id = (
                 SELECT id FROM categories
                 WHERE name = 'Smartphones'
             ))
            OR
            (name IN ('Wireless Mouse', 'Keyboard')
             AND category_id = (
                 SELECT id FROM categories
                 WHERE name = 'Accessories'
             ))
    """)

    op.execute("""
        DELETE FROM categories
        WHERE name IN ('Smartphones', 'Accessories')
    """)
