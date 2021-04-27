from pyquery import PyQuery
from typing import TypedDict, List
from client import CMCGClient, DataSourceConfig

class IndicacaoConfig(TypedDict):
    numindic: str
    dataprotent: str
    dataano: str
    origemdoc: str
    assuntodoc: str


class Tramite(TypedDict):
    data: str
    hora: str
    texto: str
    anotacoes: str


class Indicacao(TypedDict):
    autor: str
    protocolo: str
    tramites: List[Tramite]


class IndicacaoClient(CMCGClient):
    __ds_config: DataSourceConfig = {
        "LBWEB_BASENAME": "SIL4_005MS",
        "LBWEB_UDBNAME": "DEFUDB",
        "LBWEB_SERVERNAME": "LOCALHOST",
        "LBWEB_SESSIONTIMEOUT": "5",
        "LBWEB_RECORDSPERPAGE": "10",
        "LBWEB_NOSHOWALLRECORDS": "ok",
        "LBWEB_USERNAME": "164FWT405XKYCGST",
        "LBWEB_PASSWORD": "164FWT405XKYCGST",
        "LBWEB_OPENSESSION": "ok",
        "LBWEB_RUNQBF": "Consultar",
    }

    records_per_page: int = __ds_config['LBWEB_RECORDSPERPAGE']

    def __init__(self, query_config: IndicacaoConfig, opt_ds_config: DataSourceConfig = None) -> None:
        if opt_ds_config is None:
            opt_ds_config = {}
        super(IndicacaoClient, self).__init__(
            uri='/consulta-indic-lista.lbsp',
            ds_config={
                **IndicacaoClient.__ds_config,
                **opt_ds_config
            },
            query_config=query_config
        )


def find_total_count(html: str) -> str:
    d = PyQuery(html)
    count = d('div[class="w3-col w3-half w3-left-align w3-small"] p').text()
    return count


def find_total_pages(html: str) -> int:
    d = PyQuery(html)
    count = d('div[class="w3-col w3-half w3-left-align w3-small"] span[class="w3-text-blue"]:last').text()
    return int(count)


def find_indicacoes(html: str) -> List[Indicacao]:
    d = PyQuery(html)
    indicacoes = []
    current_index = 0

    for heading in d.items('div[class="w3-col w3-left-align"] > p > b'):
        indicacoes.append(dict({
            "heading": heading.text(),
        }))

    for content in d.items('div#Demo1'):
        autor = content('div[class="w3-col w3-left w3-twothird"]').remove('label').remove('br').text()
        protocolo = content('div[class="w3-col w3-left w3-third"]').remove('label').remove('br').text()
        tramites = []
        tramite_idx = 0
        for content_row in content.items('div[class="w3-row-padding"]'):
            for col in content_row.items('div[class="w3-col w3-left w3-quarter"]'):
                text = col.text()
                if text not in ['Data de Trâmite', 'Hora de Trâmite', 'Trâmite', 'Anotações']:
                    if tramite_idx == 0:
                        tramites.append([text])
                    else:
                        tramites[-1].append(text)
                    tramite_idx += 1
                    if tramite_idx == 4:
                        tramite_idx = 0

        indicacoes[current_index] = {
            **indicacoes[current_index],
            "autor": autor,
            "protocolo": protocolo,
            "tramites": [{
                "data": tramite[0],
                "hora": tramite[1],
                "texto": tramite[2],
                "anotacoes": tramite[3]
            } for tramite in tramites],
        }
        current_index += 1

    return indicacoes


def scrap(numero: str, data_entrada: str, ano: str, autor: str, assunto: str):
    records_per_page = 500
    client = IndicacaoClient(
        IndicacaoConfig(
            numindic=numero,
            dataprotent=data_entrada,
            dataano=ano,
            origemdoc=autor,
            assuntodoc=assunto
        ),
        DataSourceConfig(
            LBWEB_RECORDSPERPAGE=records_per_page
        )
    )

    print('Client inicializado')
    initial_doc = client.start()
    total_count = find_total_count(initial_doc)
    total_pages = find_total_pages(initial_doc)
    indicacoes = find_indicacoes(initial_doc)
    for _ in range(total_pages):
        indicacoes = indicacoes + find_indicacoes(client.next())

    return indicacoes
