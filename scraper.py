from pyquery import PyQuery
from typing import TypedDict, List


class Tramite(TypedDict):
    data: str
    hora: str
    texto: str
    anotacoes: str


class Indicacao(TypedDict):
    autor: str
    protocolo: str
    tramites: List[Tramite]


def scrap_indicacao(html: str) -> List[Indicacao]:
    d = PyQuery(html)
    # print()
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
                print(text)
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
