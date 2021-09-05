import json
import logging
import os.path

from sarracenia.flowcb import FlowCB
from sarracenia.flowcb.gather import msg_dumps
import GTStoWIS2

logger = logging.getLogger(__name__)



class Wistree(FlowCB):
    """
       Given a file whose name begins with a WMO GTS AHL
       (World Meteorological Organization, Global Telecommunications' System, Abbreviated Header Line)
       map the given AHL to a WIS-compliant topic tree. (WIS-WMO Information Service.)

       So when downloading, instead of writing the file to a single directory, it is
       written to a WIS-compliant folder structure.
    """

    def __init__(self, options):

        # FIXME: should a logging module have a logLevel setting?
        #        just put in a cookie cutter for now...
        if hasattr(options, 'logLevel'):
            logger.setLevel(getattr(logging, options.logLevel.upper()))
        else:
            logger.setLevel(logging.INFO)

        self.topic_builder=GTStoWIS2.GTStoWIS2()
        self.o = options


    def after_accept(self, worklist):

        new_incoming=[]

        for msg in worklist.incoming:

            # /20181218/UCAR-UNIDATA/WMO-BULLETINS/IX/21/IXTD99_KNES_182147_9d73fc80e12fca52a06bf41c716cd718

            try:
                # fix file name suffix.
                type_suffix = self.topic_builder.mapAHLtoExtension(msg['new_file'][0:2] )

                # /20181218/UCAR-UNIDATA/WMO-BULLETINS/IX/21/IXTD99_KNES_182147_9d73fc80e12fca52a06bf41c716cd718.cap
                tpfx=msg['subtopic']
    
                # input has relpath=/YYYYMMDD/... + pubTime
                # need to move the date from relPath to BaseDir, adding the T hour from pubTime.
                new_baseSubDir=tpfx[0]+msg['pubTime'][8:11]
                t='.'.join(tpfx[0:2])+'.'+new_baseSubDir
                new_baseDir = msg['new_dir'] + os.sep + new_baseSubDir
                new_relDir = 'WIS' + os.sep + self.topic_builder.mapAHLtoTopic(msg['new_file'])

                if msg['new_file'][-len(type_suffix):] != type_suffix:
                   new_file = msg['new_file']+type_suffix
                else:
                   new_file = msg['new_file']

                self.o.set_newMessageUpdatePaths( msg, new_baseDir + os.sep + new_relDir, new_file )

            except Exception as ex:
                logger.error( "failed to map %s to a topic, skipped." % msg['new_file'] , exc_info=True )
                worklist.failed.append(msg)
                continue
    
            # remove some legacy fields in the messages, to de-clutter.
            msg['_deleteOnPost'] |= set( [ 'from_cluster', 'sum', 'to_clusters', 'sundew_extension', 'filename', 'source',  ] )
            new_incoming.append(msg)

        worklist.incoming=new_incoming 
