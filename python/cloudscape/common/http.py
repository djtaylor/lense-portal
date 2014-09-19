# CloudScape Libraries
from cloudscape.common.collection import Collection

# HTTP Headers
HEADER = Collection({
    'API_USER':     'CS-API-User',
    'API_KEY':      'CS-API-Key',
    'API_TOKEN':    'CS-API-Token',
    'API_GROUP':    'CS-API-Group',
    'CONTENT_TYPE': 'Content-Type',
    'ACCEPT':       'Accept' 
}).get()

# MIME Types
MIME_TYPE = Collection({
    'TEXT': {
        'HTML':         'text/html',
        'CSS':          'text/css',
        'CSV':          'text/csv',
        'PLAIN':        'text/plain',
        'RTF':          'text/rtf'
    },
    'APPLICATION': {
        'XML':          'application/xml',
        'JSON':         'application/json',
        'STREAM':       'application/octet-stream',
        'OGG':          'application/ogg',
        'POSTSCRIPT':   'application/postscript',
        'RDF_XML':      'application/rdf+xml',
        'RSS_XML':      'application/rss+xml',
        'SOAP_XML':     'application/soap+xml',
        'FONT_WOFF':    'application/font-woff',
        'XHTML_XML':    'application/xhtml+xml',
        'ATOM_XML':     'application/atom+xml',
        'XML':          'application/xml',
        'XML_DTD':      'application/xml-dtd',
        'ECMASCRIPT':   'application/ecmascript',
        'PDF':          'application/pdf',
        'ZIP':          'application/zip',
        'GZIP':         'application/gzip',
        'JAVASCRIPT':   'application/javascript'
    }
}).get()