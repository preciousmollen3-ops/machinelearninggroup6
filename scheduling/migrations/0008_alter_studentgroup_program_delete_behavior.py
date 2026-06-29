from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("scheduling", "0007_remove_course_program_course_department_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'scheduling_studentgroup'
                ) THEN
                    ALTER TABLE scheduling_studentgroup
                    DROP CONSTRAINT IF EXISTS scheduling_studentgr_program_id_0e785061_fk_schedulin;

                    ALTER TABLE scheduling_studentgroup
                    ADD CONSTRAINT scheduling_studentgr_program_id_0e785061_fk_schedulin
                    FOREIGN KEY (program_id)
                    REFERENCES scheduling_program(id)
                    ON DELETE CASCADE;
                END IF;
            END $$;
            """,
            reverse_sql="""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'scheduling_studentgroup'
                ) THEN
                    ALTER TABLE scheduling_studentgroup
                    DROP CONSTRAINT IF EXISTS scheduling_studentgr_program_id_0e785061_fk_schedulin;

                    ALTER TABLE scheduling_studentgroup
                    ADD CONSTRAINT scheduling_studentgr_program_id_0e785061_fk_schedulin
                    FOREIGN KEY (program_id)
                    REFERENCES scheduling_program(id);
                END IF;
            END $$;
            """,
        ),
    ]
