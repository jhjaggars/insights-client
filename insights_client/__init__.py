#!/usr/bin/python
"""
 Gather and upload Insights data for
 Red Hat Insights
"""
import sys
import subprocess
import logging

logging.basicConfig()

__author__ = 'Richard Brantley <rbrantle@redhat.com>, Jeremy Crafts <jcrafts@redhat.com>, Dan Varga <dvarga@redhat.com>'

EGGS = [
    "/var/lib/insights/newest.egg",
    "/var/lib/insights/last_stable.egg",
    "/etc/insights-client/rpm.egg"
]


def go(phase, eggs, inp=None):
    """
    Call the run script for the given phase.  If the phase succeeds returns the
    index of the egg that succeeded to be used in the next phase.
    """
    insights_command = ["insights-client-run"] + sys.argv[1:]
    for egg in eggs:
        logging.debug("Attempting %s with %s", phase, egg)
        process = subprocess.Popen(insights_command, stdout=subprocess.PIPE, stdin=inp, env={
            "INSIGHTS_PHASE": str(phase),
            "PYTHONPATH": str(egg)
        })
        stdout, stderr = process.communicate(inp)
        if stderr:
            logging.error("%s failed with: %s", phase, stderr)
        if process.return_code == 0:
            logging.info("%s completed with: %s", stdout)
            return stdout


def _main():
    """
    attempt to update with current, fallback to rpm
    attempt to collect and upload with new, then current, then rpm
    if an egg fails a phase never try it again
    """

    go('update', EGGS[1:])
    response = go('collect', EGGS)
    if response is not None:
        go('upload', EGGS, response)

if __name__ == '__main__':
    _main()
