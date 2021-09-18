from datetime import datetime
from typing import Tuple

import scrapy


class VolumeSpider(scrapy.Spider):
    name = 'volume'
    start_urls = [
        'https://center.vodafone.de/vfcenter/index.html'
    ]

    @staticmethod
    def format_volume(volume: str) -> float:
        '''Takes raw volume string and returns
        volume as float in GB.'''
        if volume.endswith('GB'):
            volume = volume[:-2]
        else:
            raise NotImplementedError(f'Could not parse volumne, {volume}')
        return float(volume.replace(',', '.'))

    @staticmethod
    def format_dates(dates: str) -> Tuple[datetime, datetime]:
        '''Takes raw dates string and returns
        start and end date of billing period.

        Usual format is "05.09.-04.10.2021". '''
        start, end = dates.split('-')

        # if no year available, add year information from end date
        if len(start.split('.')[-1]) != 4:
            start = start + end.split('.')[-1]

        start = datetime.strptime(start, r'%d.%m.%Y')
        end = datetime.strptime(end, r'%d.%m.%Y')

        return start, end

    def parse(self, response):
        current, total, dates, *_ = response.css('div.fr::text').getall()

        current = VolumeSpider.format_volume(current)
        total = VolumeSpider.format_volume(total)
        start_date, end_date = VolumeSpider.format_dates(dates)

        yield {
            'current_volume': current,
            'total_volume': total,
            'start_date': start_date,
            'end_date': end_date,
            'timestamp': datetime.now()
        }
