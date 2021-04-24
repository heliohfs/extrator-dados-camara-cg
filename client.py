import requests
from requests import Response
from threading import Lock
from typing import TypedDict

DataSourceConfig = TypedDict('DataSourceConfig',
                             {
                                 'LBWEB_BASENAME': str,
                                 'LBWEB_UDBNAME': str,
                                 'LBWEB_SERVERNAME': str,
                                 'LBWEB_SESSIONTIMEOUT': str,
                                 'LBWEB_RECORDSPERPAGE': str,
                                 'LBWEB_NOSHOWALLRECORDS': str,
                                 'LBWEB_USERNAME': str,
                                 'LBWEB_PASSWORD': str,
                                 'LBWEB_OPENSESSION': str,
                                 'LBWEB_RUNQBF': str,
                             })

IndicacaoConfig = TypedDict('IndicacaoConfig',
                            {
                                'numindic': str,
                                'dataprotent': str,
                                'dataano': str,
                                'origemdoc': str,
                                'assuntodoc': str
                            })

ProjetoDeLeiConfig = TypedDict('ProjetoDeLeiConfig',
                               {
                                   'projet': str,
                                   'dataano': str,
                                   'tipoprojeto': str,
                                   'emenda': str,
                                   'tipoemenda': str,
                                   'origemdoc': str,
                                   'tipocom': str,
                                   'assuntodoc': str,
                                   'textoprojet': str,
                               })


class SingletonMeta(type):
    _instances = {}

    _lock: Lock = Lock()

    def __call__(self, *args, **kwargs):
        with self._lock:
            if self not in self._instances:
                instance = super().__call__(*args, **kwargs)
                self._instances[self] = instance
        return self._instances[self]


class CMCGClient(metaclass=SingletonMeta):
    __host = 'https://sgl.camara.ms.gov.br'

    def __init__(self, uri: str, ds_config: DataSourceConfig, query_config: dict) -> None:
        self.__uri = uri
        self.__ds_config = ds_config
        self.__query_config = query_config
        self.__session_cookie = None

    def fetch(self, data=None) -> Response:
        if data is None:
            data = {}
        if self.__session_cookie is None:
            r = requests.post(
                url=CMCGClient.__host + self.__uri,
                data={
                    **self.__query_config,
                    **self.__ds_config,
                    **data
                }
            )
        else:
            r = requests.post(
                url=CMCGClient.__host + self.__uri,
                data={
                    **data
                },
                cookies={
                    'COOKIE': self.__session_cookie
                }
            )

        if r.cookies['COOKIE']:
            self.__session_cookie = r.cookies['COOKIE']

        return r

    def start(self) -> str:
        r = self.fetch()
        return r.text

    def next(self) -> str:
        r = self.fetch({
            'LBWEB_COOKIE': self.__session_cookie,
            'LBWEB_NEXTPAGE': '>'
        })
        return r.text


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

    def __init__(self, query_config: IndicacaoConfig) -> None:
        super(IndicacaoClient, self).__init__(
            uri='/consulta-indic-lista.lbsp',
            ds_config=IndicacaoClient.__ds_config,
            query_config=query_config
        )
