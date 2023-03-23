import os
import subprocess
from typing import List


class PsqlRuner:
    def __init__(self, login, password, host, port, db, path) -> None:
        self.login = login
        self.password = password
        self.host = host
        self.port = port
        self.db = db
        self.path = path

    def _connstr(self) -> str:
        return f"postgresql://{self.login}:{self.password}@{self.host}:{self.port}/{self.db}"

    def runcmd(self, params: List[str]):
        cmd = ["psql", self._connstr()]
        cmd.extend(params)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=self.path)
        output, error = process.communicate()
        return (output, error)


class DataApply:

    def run_setup_db(self):

        login = "jovyan"
        password = "jovyan"
        host = "localhost"
        port = "5432"
        db = "de"
        # proj_path = "vsc-pg-metabase/sprint-1/project/task2/setup"
        proj_path = os.path.dirname(os.path.abspath(__file__))

        runer = PsqlRuner(login, password, host, port, db, proj_path)

        print("------------------UPDATING SCHEMA------------------")
        ddl_cmd = ["-f", "setup_db.sql"]
        (output, error) = runer.runcmd(ddl_cmd)
        print(output)
        print(error)
        print("LOADING FINISHED SUCCESSFULLY.")
