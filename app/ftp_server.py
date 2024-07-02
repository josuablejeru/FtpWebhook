# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
An example FTP server with minimal user authentication.
"""

import requests

from twisted.cred.checkers import AllowAnonymousAccess
from twisted.cred.portal import Portal
from twisted.internet import reactor, defer
from twisted.internet.interfaces import IConsumer
from twisted.protocols.ftp import (
    FTPFactory,
    FTPRealm,
    IFTPShell,
    FTPShell,
    errnoToFailure,
    IWriteFile,
)
from twisted.python import usage
from zope.interface import implementer

import sys


class Options(usage.Options):
    optParameters = [
        ["port", "p", 21, "The port number to listen on", int],
        ["root", "r", "./upload", "The root directory for the FTP server"],
        ["webhook", "w", None, "The webhook URL to send uploaded files to"],
    ]


@implementer(IConsumer)
class FileWebhookConsumer:
    webhook_url = None  # This will be set from the CLI

    def __init__(self, fObj) -> None:
        self.fObj = fObj

    def registerProducer(self, producer, streaming):
        self.producer = producer
        assert streaming

    def unregisterProducer(self):
        self.producer = None
        self.fObj.close()

    def write(self, bytes):
        if self.webhook_url:
            requests.post(
                self.webhook_url,
                data=bytes,
            )
        else:
            print("No webhook URL provided. Skipping webhook call.")


@implementer(IWriteFile)
class FileWriter:
    def __init__(self, fObj):
        self.fObj = fObj
        self._receive = False

    def receive(self):
        assert not self._receive, "Can only call IWriteFile.receive *once* per instance"
        self._receive = True
        # FileConsumer will close the file object
        return defer.succeed(FileWebhookConsumer(self.fObj))

    def close(self):
        return defer.succeed(None)


# Custom FTP Shell to override openForWriting
@implementer(IFTPShell)
class CustomFTPShell(FTPShell):
    def __init__(self, root):
        self.root = root
        super().__init__(filesystemRoot=self.root)

    def openForWriting(self, path):
        """
        Open C{path} for writing.

        @param path: The path, as a list of segments, to open.
        @type path: C{list} of C{unicode}
        @return: A L{Deferred} is returned that will fire with an object
            implementing L{IWriteFile} if the file is successfully opened.  If
            C{path} is a directory, or if an exception is raised while trying
            to open the file, the L{Deferred} will fire with an error.
        """
        p = self._path(path)
        if p.isdir():
            # Normally, we would only check for EISDIR in open, but win32
            # returns EACCES in this case, so we check before
            return defer.fail(IsADirectoryError(path))
        try:
            fObj = p.open("w")
        except OSError as e:
            return errnoToFailure(e.errno, path)
        except BaseException:
            return defer.fail()
        return defer.succeed(FileWriter(fObj))


class CustomFTPRealm(FTPRealm):
    def requestAvatar(self, avatarId, mind, *interfaces):
        if IFTPShell in interfaces:
            return IFTPShell, CustomFTPShell(self.anonymousRoot), lambda: None
        raise NotImplementedError()


def main(config):
    root = config["root"]
    port = config["port"]
    webhook_url = config["webhook"]

    # Update FileWebhookConsumer to use the provided webhook URL
    FileWebhookConsumer.webhook_url = webhook_url

    p = Portal(CustomFTPRealm(root), [AllowAnonymousAccess()])
    f = FTPFactory(p)
    f.timeOut = 4800  # seconds
    f.passivePortRange = range(50000, 50010)

    reactor.listenTCP(port, f)
    reactor.run()


if __name__ == "__main__":
    options = Options()
    try:
        options.parseOptions()
    except usage.UsageError as errortext:
        print(f"{sys.argv[0]}: {errortext}")
        print(f"{sys.argv[0]}: Try --help for usage details.")
        sys.exit(1)

    main(options)
