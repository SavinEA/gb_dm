import requests
from pathlib import Path
import time
import json
import cw_1


class Parser5kaHW(cw_1.Parser5ka):

    def __init__(self, start_url: str, categories_url: str, save_path: Path):
        super().__init__(start_url, save_path)
        self.categories_url = categories_url

    def _get_response(self, url, parameters):
        while True:
            response = requests.get(url, headers=self.headers, params={'categories': parameters})
            if response.status_code == 200:
                return response
            time.sleep(0.5)

    def _parse(self, url: str, parameters):
        while url:
            response = self._get_response(url, parameters)
            data: dict = response.json()
            url = data ['next']
            for product in data['results']:
                yield product

    def run(self):
        categories = self._get_response(self.categories_url, None)
        categories_data: dict = categories.json()
        for cat in categories_data:
            categories_list = []
            product_path = self.save_path.joinpath(f"{cat['parent_group_name']}.json")
            for product in self._parse(self.start_url, cat['parent_group_code']):
                categories_list.append(product)
            self._save(categories_list, cat['parent_group_name'], cat['parent_group_code'], product_path)

    def _save(self, data: dict, name, code, file_path: Path):
        with open(file_path, 'a', encoding='utf-8') as file:
            file.write('{' + f'"name": "{name}",'
                             f'"code": {code},'
                             f'"products": {json.dumps(data, ensure_ascii=False)}' + '}')


if __name__ == '__main__':
    url_main = 'https://5ka.ru/api/v2/special_offers/'
    url_categories = 'https://5ka.ru/api/v2/categories/'
    save_path = Path(__file__).parent.joinpath('categories')
    if not save_path.exists():
        save_path.mkdir()

    parser = Parser5kaHW(url_main, url_categories, save_path)
    parser.run()
