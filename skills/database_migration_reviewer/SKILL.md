---
name: database_migration_reviewer
version: 1.0.0
description: Systematic review routine for inspecting database migrations for safety, correctness, locking risks, and rollback integrity.
author: kuroLabs-ai
tags: [database, migrations, sql, alembic, prisma, flyway, safety, review]
---

# Database Migration Reviewer Skill Routine

Systematic safety inspection procedure for reviewing proposed database migrations (Alembic, Prisma, Flyway, Django, Liquibase, raw SQL) before they are applied to staging or production environments.

## Overview
Database migrations are one of the highest-risk operations in production deployments. A single non-reversible migration, table lock, or missing index can cause hours of downtime. This routine ensures every migration is safe, idempotent, performant, and properly reversible.

## Routine Steps:

1. **Migration File Discovery & Classification**:
   - Identify the migration framework in use (Alembic `versions/`, Prisma `migrations/`, Flyway `sql/`, Django `migrations/`, or raw `.sql` scripts).
   - Locate migration files that are pending (not yet applied to the target environment).
   - Classify each migration as: `schema_change`, `data_migration`, `index_change`, `constraint_change`, or `backfill`.

2. **Locking Risk Inspection**:
   - **Critical operations to flag**:
     - Adding a non-nullable column WITHOUT a DEFAULT value to an existing populated table (requires full table rewrite in PostgreSQL).
     - `ALTER TABLE ... ADD CONSTRAINT` with immediate validation (use `NOT VALID` + `VALIDATE CONSTRAINT` in two separate steps instead).
     - `ALTER TABLE ... ALTER COLUMN TYPE` that cannot be cast automatically (requires full table rewrite).
     - `DROP TABLE`, `TRUNCATE`, or `DROP COLUMN` on tables with active foreign key references.
     - Long-running `UPDATE` batches on large tables without batching strategy (prefer paginated batch updates).
   - Recommend safe alternatives for every flagged pattern.

3. **Rollback & Downgrade Integrity Check**:
   - Verify that the migration has a valid `downgrade()` function (Alembic), `down()` (Prisma), or a corresponding rollback SQL file.
   - Confirm the downgrade is idempotent: can it be safely re-applied without errors if run multiple times?
   - Verify that dropped tables or columns are backed up or that data is recoverable from the downgrade script.
   - Flag any irreversible operations (e.g. `DROP TABLE` without backup, column type coercions that lose precision) with `IRREVERSIBLE WARNING`.

4. **Index & Constraint Validation**:
   - Check that every new foreign key column has a corresponding index created (missing FK indexes cause sequential scans on joins).
   - Verify new unique constraints or indexes are created `CONCURRENTLY` in PostgreSQL to avoid write locks.
   - Inspect composite indexes for correct column ordering matching the most common query `WHERE` clauses.

5. **Data Integrity & Seed Verification**:
   - For data migrations: confirm row count expectations and that `WHERE` clauses correctly scope the update to target rows only.
   - Verify that enum additions, type changes, or column renames have corresponding ORM model or schema updates in application code.
   - Check for hardcoded environment-specific values (e.g. hardcoded production user IDs or URLs) that should be parameterized.

6. **Final Report & Approval Checklist**:
   - Compile a structured migration report listing:
     - **PASS** items: migrations reviewed and cleared.
     - **WARN** items: non-blocking but recommended improvements.
     - **BLOCK** items: critical issues that must be resolved before applying to production.
   - Suggest the safe migration execution order if multiple migrations are pending.
