from neo4j import GraphDatabase

from . import config

_driver = None


def driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USER, config.NEO4J_PASSWORD),
            notifications_min_severity="OFF",
        )
    return _driver


def run(query: str, **params):
    """Jalankan query Cypher dan kembalikan list of dict."""
    records, _, _ = driver().execute_query(
        query, params, database_=config.NEO4J_DATABASE
    )
    return [r.data() for r in records]


def close():
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None
