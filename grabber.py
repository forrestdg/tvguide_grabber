#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Duong Dang"
__version__ = "0.1"

import logging, sys, re
import urllib2
from BeautifulSoup import BeautifulSoup
from xml.dom.minidom import Document

logger = logging.getLogger("vtv4.py")




def main():
    import optparse
    parser = optparse.OptionParser(
        usage='\n\t%prog [options]',
        version='%%prog %s' % __version__)
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="be verbose")

    parser.add_option("-d", "--date", type = "string",
                      action="store", dest="date", help="date to be grabbed")

    parser.add_option("-i", "--id", type = "string",
                      action="store", dest="id", default="vtv4",
                      help="cannal id")

    parser.add_option("-o", "--output", type = "string",
                      action="store", dest="output",
                      help="xml to be written to")

    (options, args) = parser.parse_args(sys.argv[1:])
    if not options.date:
        parser.error("Date argument missing")

    year = options.date[0:4]
    month = options.date[4:6]
    day = options.date[6:]

    if options.id != "vtv4":
        parser.error("Only channel vtv4 supported in this script")

    if not options.output:
        options.output = "%s_%s.xml"%(options.id,options.date)
    outf = open(options.output,'w')
    outf.write('')
    url = "http://vtv.vn/LichPS/GetLichPhatsong?nam=%s&thang=%s&ngay=%s&kenh=VTV4"%(year,month,day)
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)

    doc = Document()
    doc.doctype = "http://www.kazer.org/xmltv.dtd"
    tv = doc.createElement('tv')
    tv.setAttribute("generator-info-name", "grabber.py")
    doc.appendChild(tv)
    chan = doc.createElement('channel')
    chan.setAttribute('id','vtv4')
    chan_name = doc.createElement('display-name')
    chan_name.setAttribute('lang','vi')
    text = doc.createTextNode('VTV 4')
    chan_name.appendChild(text)
    chan.appendChild(chan_name)

    tv.appendChild(chan)

    for prog in soup('tr'):
        timenode = prog('td')[0]
        titlenode = prog('td')[1]
        t=timenode.text
        m = re.search(r"(?P<HOUR>\d+)h\s*:\s*(?P<MINUTE>\d+)",t)
        if not m:
            continue
        hour=m.group('HOUR')
        minute = m.group('MINUTE')
        titlex = titlenode.find('strong').text
        descx = titlenode.contents[4]
        descx = re.sub(r"^\s*","",descx)

        programme = doc.createElement("programme")
        programme.setAttribute('start',"%s%s%s +0700"
                              %(options.date,hour,minute))
        programme.setAttribute('channel', options.id)
        title = doc.createElement('title')
        title.setAttribute('lang','vi')
        text = doc.createTextNode(titlex)
        title.appendChild(text)
        programme.appendChild(title)
        if titlenode.text !="":
            desc = doc.createElement('desc')
            desc.setAttribute('lang','vi')
            if descx != "":
                text = doc.createTextNode(descx)
                desc.appendChild(text)
                programme.appendChild(desc)
        tv.appendChild(programme)

    outf.write(doc.toprettyxml(indent="  ").encode("utf-8"))
    outf.close()

if __name__ == '__main__':
    main()
