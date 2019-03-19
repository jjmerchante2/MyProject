# import threading
# import worker
import sqlite3
import time
from mordred.mordred import run_mordred


class MordredManager:
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.cursor = self.conn.cursor()

    def _db_update(self, query):
        res = self.cursor.execute(query)
        self.conn.commit()
        return res

    def _db_select(self, query):
        res = self.cursor.execute(query)
        row = res.fetchone()
        return row

    def run(self):
        waiting_msg = True
        while True:
            if waiting_msg is True:
                print('Waiting for new repositories...')
                waiting_msg = False
            q = "SELECT url, gh_token_id FROM CauldronApp_task WHERE status = 'PENDING' ORDER BY last_modified;"
            row = self._db_select(q)
            if row is not None:
                url = row[0]
                id_user = row[1]
                print("Analyzing", url)

                q = "SELECT token FROM CauldronApp_GithubToken WHERE id = {};".format(id_user)
                row = self._db_select(q)
                token = row[0]

                q = "UPDATE CauldronApp_task SET status = 'RUNNING' WHERE url='{}';".format(url)
                self._db_update(q)
                try:
                    run_mordred(repo=url, gh_token=token)
                except Exception:
                    q = "UPDATE CauldronApp_task SET status = 'ERROR' WHERE url='{}';".format(url)
                    self._db_update(q)

                q = "UPDATE CauldronApp_task SET status = 'COMPLETED' WHERE url='{}';".format(url)
                self._db_update(q)
                waiting_msg = True

            time.sleep(1)


if __name__ == "__main__":
    manager = MordredManager('../db.sqlite3')
    manager.run()
