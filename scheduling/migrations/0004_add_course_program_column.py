from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("scheduling", "0003_timeslot_course_difficulty_score_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE scheduling_course
                ADD COLUMN IF NOT EXISTS program_id bigint REFERENCES scheduling_program(id);
            """,
            reverse_sql="""
                ALTER TABLE scheduling_course
                DROP COLUMN IF EXISTS program_id;
            """,
        ),
    ]
