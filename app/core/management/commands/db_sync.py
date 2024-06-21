import time
from psycopg2 import OperationalError as PsyOpError
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.stdout.write("-Waiting for the database to be ready-")
        ready = False
        while not ready:
            try:
                self.check(databases=['default'])
                ready = True
            except(PsyOpError, OperationalError):
                time.sleep(1)

        self.stdout.write("-Database available-")
