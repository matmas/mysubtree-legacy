from subprocess import PIPE, STDOUT
import subprocess

def uglifyjs(filedata):
    uglifyjs_with_args = ["uglifyjs", "--no-copyright"]
    process = subprocess.Popen(uglifyjs_with_args, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    output = process.communicate(input=filedata)[0]
    return output
