from indicacoes import scrap
import json

if __name__ == '__main__':
    indicacoes = scrap(
        numero='',
        data_entrada='',
        ano='2021',
        autor='',
        assunto=''
    )

    with open('data.json', 'w') as outfile:
        json.dump(indicacoes, outfile)
