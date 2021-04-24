from client import IndicacaoClient
from scraper import scrap_indicacao

if __name__ == '__main__':
    client = IndicacaoClient(
        query_config={
            'numindic': '',
            'dataprotent': '',
            'dataano': '2021',
            'origemdoc': '',
            'assuntodoc': ''
        }
    )

    scrap_indicacao(client.start())
