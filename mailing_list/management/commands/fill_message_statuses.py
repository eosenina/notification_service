import json

from django.core.management import BaseCommand, CommandError

from mailing_list.models import MessageStatus


class Command(BaseCommand):
    help = 'Adds statuses of sending messages to the table mailing_list_messagestatus'

    def handle(self, *args, **options):
        stat_count = MessageStatus.objects.count()
        if stat_count != 0:
            self.stdout.write(self.style.SUCCESS('Table messagestatuses is not empty already.'))
            return

        with open('mailing_list/messagestatuses.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        for line in data:
            try:
                new_stat = MessageStatus.objects.create(name=line['fields']['name'],
                                                        pk=line['pk'])
                new_stat.save()
            except Exception as e:
                raise CommandError('Could not create message status: {}'.format(e))

        self.stdout.write(self.style.SUCCESS('Message statuses created.'))
