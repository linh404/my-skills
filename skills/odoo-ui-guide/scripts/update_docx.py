"""Refresh the table of contents of a DOCX with LibreOffice, save it, and export a PDF.

Run with the system Python that ships the LibreOffice UNO bridge (python3-uno):
    /usr/bin/python3 update_docx.py guide.docx [guide.pdf]
"""

import os
import subprocess
import sys
import tempfile
import time

import uno
from com.sun.star.beans import PropertyValue


def prop(name, value):
    p = PropertyValue()
    p.Name = name
    p.Value = value
    return p


def connect(pipe, attempts=60):
    local = uno.getComponentContext()
    resolver = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
    for _ in range(attempts):
        try:
            return resolver.resolve(f"uno:pipe,name={pipe};urp;StarOffice.ComponentContext")
        except Exception:
            time.sleep(0.5)
    raise RuntimeError("LibreOffice did not start")


def main():
    docx = os.path.abspath(sys.argv[1])
    pdf = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.splitext(docx)[0] + ".pdf"
    pipe = f"odoo_ui_guide_{os.getpid()}"
    profile = tempfile.mkdtemp(prefix="lo_profile_")
    office = subprocess.Popen([
        "soffice", "--headless", "--invisible", "--nologo", "--norestore",
        f"-env:UserInstallation=file://{profile}",
        f"--accept=pipe,name={pipe};urp;",
    ])
    try:
        ctx = connect(pipe)
        desktop = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
        doc = desktop.loadComponentFromURL(uno.systemPathToFileUrl(docx), "_blank", 0, (prop("Hidden", True),))
        indexes = doc.getDocumentIndexes()
        for i in range(indexes.getCount()):
            indexes.getByIndex(i).update()
        doc.refresh()
        doc.storeToURL(uno.systemPathToFileUrl(docx), (prop("FilterName", "MS Word 2007 XML"),))
        doc.storeToURL(uno.systemPathToFileUrl(pdf), (prop("FilterName", "writer_pdf_Export"),))
        doc.close(True)
        try:
            desktop.terminate()
        except Exception:
            pass
    finally:
        try:
            office.wait(timeout=20)
        except subprocess.TimeoutExpired:
            office.kill()
    print(f"docx: {docx}\npdf:  {pdf}")


if __name__ == "__main__":
    main()
