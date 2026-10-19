"""flask --app wsgi seed: demo data, the same story as the lessons (BlueLeaf Studio and Sharma Traders)."""
import click

from .extensions import db
from .models import Board, Task, Tenant, User
from .security import hash_password

# A FAKE practice password for every demo user. Never use it for anything real.
DEMO_PASSWORD = "demo-password-123"


def register(app):
    @app.cli.command("seed")
    def seed():
        """Add two demo tenants with members, a board and tasks (skipped if they exist)."""
        if db.session.scalar(db.select(Tenant).filter_by(name="BlueLeaf Studio")):
            click.echo("demo data already there")
            return
        blueleaf = Tenant(name="BlueLeaf Studio", plan="team")
        sharma = Tenant(name="Sharma Traders", plan="free")
        db.session.add_all([blueleaf, sharma])
        db.session.flush()
        pw = hash_password(DEMO_PASSWORD)
        db.session.add_all([
            User(tenant_id=blueleaf.id, email="priya@blueleaf.example", name="Priya", role="owner", password_hash=pw),
            User(tenant_id=blueleaf.id, email="arjun@blueleaf.example", name="Arjun", role="admin", password_hash=pw),
            User(tenant_id=blueleaf.id, email="meera@blueleaf.example", name="Meera", role="member", password_hash=pw),
            User(tenant_id=sharma.id, email="ravi@sharma.example", name="Ravi", role="owner", password_hash=pw),
        ])
        board = Board(tenant_id=blueleaf.id, name="Website launch")
        db.session.add(board)
        db.session.flush()
        for title, prio in [("Draw the home page", "high"), ("Pick fonts", "normal"),
                            ("Book the photo shoot", "low"), ("Write notes", "normal")]:
            db.session.add(Task(tenant_id=blueleaf.id, board_id=board.id, title=title, priority=prio))
        db.session.add(Task(tenant_id=sharma.id, title="Order stock", priority="high"))
        db.session.commit()
        click.echo(f"seeded: BlueLeaf Studio (tenant {blueleaf.id}), Sharma Traders (tenant {sharma.id}); "
                   f"every demo user's password is {DEMO_PASSWORD}")
