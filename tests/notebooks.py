# -*- encoding: utf-8 -*-
import os
import shutil
import subprocess
import sys
import tempfile


def output_sample():
    return os.path.join(base(), 'resources', 'output-sample')


def notebooks():
    return os.path.normpath(os.path.join(base(), '..', 'notebook'))


def base():
    return os.path.abspath(os.path.dirname(__file__))


def prepare_data(directory):
    source_directory = output_sample()
    for item in os.listdir(source_directory):
        source = os.path.join(source_directory, item)
        target = os.path.join(directory, item)
        if os.path.isdir(source):
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)


def notebook_env(directory):
    return dict(os.environ, **{'PRIO_BASE': directory})


def make_process(directory):
    return subprocess.Popen(['treon', notebooks()],
                            env=notebook_env(directory),
                            stderr=subprocess.PIPE,
                            encoding='utf-8')


def run(directory):
    process = make_process(directory)

    def drain_output():
        while True:
            line = process.stderr.readline()
            if not line:
                break
            print(line.strip(), file=sys.stderr)

    while True:
        try:
            drain_output()
            code = process.poll()
            if code is not None:
                break
        except KeyboardInterrupt:
            drain_output()

    sys.exit(code)


def run_notebooks():
    with tempfile.TemporaryDirectory() as temp_directory:
        prepare_data(temp_directory)
        run(temp_directory)


if __name__ == '__main__':
    run_notebooks()
