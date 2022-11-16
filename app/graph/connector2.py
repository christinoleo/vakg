import time
from contextlib import contextmanager

import yappi
from py2neo import Graph
from pyinstrument import Profiler

from credentials_ import url, login, password


class NeoSession:
    def __init__(self, url, user, password):
        self.url = url
        self.engine = Graph(self.url, auth=(user, password), user=user, password=password, init_size=2, max_size=5)

    def get_db(self):
        # t1 = time.time()
        # print(f'Time Start!')
        tx = self.engine.begin()
        try:
            yield tx
            # t2 = time.time()
            # print(f'T Time: {t2-t1}')
        except Exception as e:
            self.engine.rollback(tx)
            # t2 = time.time()
            # print(f'E Time: {t2-t1}')
            raise e
        finally:
            if not tx.closed:
                print('CLOSED', tx)
                self.engine.commit(tx)

            # t2 = time.time()
            # print(f'F Time: {t2-t1}')


def neodb():
    return Graph(url, auth=(login, password))


neodbsession = NeoSession(url, login, password)


class HelloWorldExample:
    def __init__(self, db):
        self.driver = db

    def print_greeting(self, message):
        with self.driver.get_db() as session:
            greeting = session.write_transaction(self._create_and_return_greeting, message)
            print(greeting)

    @staticmethod
    def _create_and_return_greeting(tx, message):
        result = tx.run("CREATE (a:Greeting) "
                        "SET a.message = $message "
                        "RETURN a.message + ', from node ' + id(a)",
                        message=message)
        return result.single()[0]


if __name__ == "__main__":
    greeter = HelloWorldExample(neodb)
    greeter.print_greeting("hello, world")
