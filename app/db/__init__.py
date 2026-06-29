"""Database package — SQLAlchemy engine, models, seed data, and repository.

The whole persistence layer lives here. The rest of the app talks to it through
two seams only: :class:`app.store.Store` (operational state) and
:mod:`app.db.repository` (read-only reference data).
"""
