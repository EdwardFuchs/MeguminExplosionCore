# import pip
import subprocess
import sys
from subprocess import Popen, PIPE


def check_and_install(packages):
    for package in packages:
        # pip.main(["install", package])
        p = Popen([sys.executable, '-m', 'pip', 'install', package], stdout=PIPE, stderr=PIPE)
        log, err = p.communicate()
        if p.returncode == 0:
            return True
        err = str(err).replace("\\r", "")
        err = err.split("\\n")
        errors = []
        for e in err:
            if "ERROR" in e:
                errors.append(e)
        if errors:
            raise ImportError("\n".join(errors))
        return True
