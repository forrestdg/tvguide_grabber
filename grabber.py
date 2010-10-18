#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Duong Dang"
__version__ = "0.1"

import logging, sys, re
import urllib2, datetime
import pytz
from BeautifulSoup import BeautifulSoup
from xml.dom.minidom import Document
from xml.dom.minidom import DOMImplementation

imp = DOMImplementation()
doctype = imp.createDocumentType(
    qualifiedName='tv',
    publicId='',
    systemId="http://www.kazer.org/xmltv.dtd",
)


logger = logging.getLogger("vtv4.py")
hanoitz = pytz.timezone('Etc/GMT-7')
paristz = pytz.timezone('Europe/Paris')
fmt = '%Y%m%d %H:%M:%S %z'

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

    year = int(options.date[0:4])
    month = int(options.date[4:6])
    day = int(options.date[6:])

    if options.id not in [ "vtv4", "vtv3", "vtv2", "vtv1", "vtv6", "vtv9" ]:
        parser.error("Only vtv channels supported in this script")

    if not options.output:
        options.output = "%s_%s.xml"%(options.id,options.date)
    outf = open(options.output,'w')
    outf.write('')
    url = "http://vtv.vn/LichPS/GetLichPhatsong?nam=%d&thang=%d&ngay=%d&kenh=%s"%(year,month,day,options.id)
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)

    doc = imp.createDocument(None, 'tv', doctype)
    tv = doc.lastChild
#    doc = Document()
#    tv = doc.createElement('tv')
#    doc.appendChild(tv)
    tv.setAttribute("generator-info-name", "grabber.py")
    chan = doc.createElement('channel')
    chan.setAttribute('id',options.id)
    chan_name = doc.createElement('display-name')
    chan_name.setAttribute('lang','vi')
    text = doc.createTextNode('Vietnam VTV%s'%re.search(r"\d+",options.id).group(0))
    chan_name.appendChild(text)
    chan.appendChild(chan_name)

    tv.appendChild(chan)
    last_programme = None
    last_length = None
    last_h = None
    last_m = None
    last_dt = None

    for prog in soup('tr'):
        timenode = prog('td')[0]
        titlenode = prog('td')[1]
        t=timenode.text
        m = re.search(r"(?P<HOUR>\d+)h\s*:\s*(?P<MINUTE>\d+)",t)
        if not m:
            continue
        hour = int(m.group('HOUR'))
        minute = int(m.group('MINUTE'))
        titlex = titlenode.find('strong').text
        descx = titlenode.contents[4]
        descx = re.sub(r"^\s*","",descx)
        descx = re.sub(r"\s*$","",descx)
        dt = datetime.datetime(year = year, month = month, day = day,
                               hour = hour, minute = minute,
                               tzinfo = hanoitz
                               )
        dt = dt.astimezone(paristz).strftime(fmt)
        end_dt = datetime.datetime(year = year, month = month, day = day,
                               hour = 23, minute = 59,
                               tzinfo = hanoitz
                               )
        end_dt = end_dt.astimezone(paristz).strftime(fmt)

        programme = doc.createElement("programme")
        programme.setAttribute('start', dt )
        programme.setAttribute('stop', end_dt )
        if last_programme:
            last_programme.setAttribute('stop',dt)

        programme.setAttribute('channel', options.id)
        title = doc.createElement('title')
        title.setAttribute('lang','vi')
        text = doc.createTextNode(titlex)
        title.appendChild(text)
        programme.appendChild(title)

        if descx != "":
            desc = doc.createElement('desc')
            desc.setAttribute('lang','vi')
            text = doc.createTextNode(descx)
            desc.appendChild(text)
            programme.appendChild(desc)


        category = doc.createElement('category')
        category.setAttribute('lang','en')
        text = doc.createTextNode('Unknown')
        category.appendChild(text)
        programme.appendChild(category)

        l = 23*60+59 - int(hour)*60 - int(minute)

        length = doc.createElement('length')
        length.setAttribute('units','minutes')
        text = doc.createTextNode(str(l))
        length.appendChild(text)
        programme.appendChild(length)
        if last_length:
            last_l = (int(hour) - int(last_h))*60 + int(minute) - int(last_m)
            text = doc.createTextNode(str(last_l))
            last_length.removeChild(last_length.firstChild)
            last_length.appendChild(text)


        tv.appendChild(programme)
        last_programme = programme
        last_h = hour
        last_m = minute
        last_length = length
        last_dt = dt
#    doc.writexml(outf, encoding = "UTF-8")
    outf.write(doc.toprettyxml(indent="  ", encoding = "UTF-8"))
    outf.close()

if __name__ == '__main__':
    main()
