from contextlib import contextmanager
from credentials_ import url, login, password

from neo4j import GraphDatabase


class NeoSession:
    def __init__(self, url, user, password):
        self.url = url
        self.engine = GraphDatabase.driver(self.url, auth=(user, password))

    @contextmanager
    def get_db(self):
        try:
            yield self.engine.session()
        except NameError as e:
            raise NameError('Mongodb engine not defined', e)
        finally:
            print('CLOSED')
            self.engine.close()


neodb = NeoSession(url, login, password)


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
