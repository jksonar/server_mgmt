from django.core.management.base import BaseCommand
from accounts.groups import create_user_groups

class Command(BaseCommand):
    help = 'Creates the default user groups with appropriate permissions'

    def handle(self, *args, **options):
        groups = create_user_groups()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created Admin group with {groups["admin"].permissions.count()} permissions'))
        self.stdout.write(self.style.SUCCESS(f'Successfully created Manager group with {groups["manager"].permissions.count()} permissions'))
        self.stdout.write(self.style.SUCCESS(f'Successfully created Viewer group with {groups["viewer"].permissions.count()} permissions'))