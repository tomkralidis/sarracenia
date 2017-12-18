#!/bin/bash

function application_dirs {
python3 << EOF
import appdirs

cachedir  = appdirs.user_cache_dir('sarra','science.gc.ca')
cachedir  = cachedir.replace(' ','\ ')
print('export CACHEDIR=%s'% cachedir)

confdir = appdirs.user_config_dir('sarra','science.gc.ca')
confdir = confdir.replace(' ','\ ')
print('export CONFDIR=%s'% confdir)

logdir  = appdirs.user_log_dir('sarra','science.gc.ca')
logdir  = logdir.replace(' ','\ ')
print('export LOGDIR=%s'% logdir)

EOF
}

eval `application_dirs`

sr stop

sr cleanup 

echo extra lines for the sr_cpump cleanup hanging
sleep 10
killall sr_cpump
echo remove these 2 when corrected

echo "cleanup trivial http server... "
if [ -f .httpserverpid ]; then
   httpserverpid="`cat .httpserverpid`"
   if [ "`ps ax | awk ' $1 == '${httpserverpid}' { print $1; }; '`" ]; then
       kill $httpserverpid
       echo "web server stopped."
       sleep 2
   else
       echo "no web server found running"
   fi
   if [ "`netstat -an | grep LISTEN | grep 8000`" ]; then
       pid="`ps ax | grep trivialserver.py | grep -v grep| awk '{print $1;};'`" 
       echo "killing rogue web server found on port 8000 at pid=$pid"
       if [ "$pid" ]; then
          kill -9 $pid
       else
          echo "ERROR: could not find web server, but it's running. Look out!"
       fi
  fi
fi

echo "cleanup trivial ftp server... "
if [ -f .ftpserverpid ]; then
   ftpserverpid="`cat .ftpserverpid`"
   if [ "`ps ax | awk ' $1 == '${ftpserverpid}' { print $1; }; '`" ]; then
       kill $ftpserverpid
       echo "ftp server stopped."
       sleep 2
   else
       echo "no properly started ftp server found running"
   fi
   if [ "`netstat -an | grep LISTEN | grep 2121`" ]; then
       pid="`ps ax | grep ftpdlib | grep -v grep| awk '{print $1;};'`" 
       echo "killing rogue ftp server on port 2121 found at pid=$pid"
       if [ "$pid" ]; then
          kill -9 $pid
       else
          echo "ERROR: could not find FTP server, but it's running. Look out!"
       fi
  fi
fi

remove_if_present=".ftpserverpid .httpserverpid aaa.conf bbb.inc checksum_AHAH.py sr_http.test.anonymous"

rm -f ${remove_if_present}


adminpw="`awk ' /bunnymaster:.*\@localhost/ { sub(/^.*:/,""); sub(/\@.*$/,""); print $1; exit; }; ' "$CONFDIR"/credentials.conf`"

queues_to_delete="`rabbitmqadmin -H localhost -u bunnymaster -p ${adminpw} -f tsv list queues | awk ' ( NR > 1 ) { print $1; }; '`"


for q in $queues_to_delete; do
    rabbitmqadmin -H localhost -u bunnymaster -p "${adminpw}" delete queue name=$q
done

exchanges_to_delete="`rabbitmqadmin -H localhost -u bunnymaster -p ${adminpw} -f tsv list exchanges | awk ' ( $1 ~ /x.*/ ) { print $1; }; '`"
for exchange in $exchanges_to_delete ; do 
   echo "deleting $exchange"
   rabbitmqadmin -H localhost -u bunnymaster -p ${adminpw} -f tsv delete exchange name=${exchange} 
done

 
flow_confs="`cd ../sarra/examples; ls */*f[0-9][0-9].conf`"
flow_incs="`cd ../sarra/examples; ls */*f[0-9][0-9].inc`"

echo $flow_incs $flow_confs | sed 's/ / ; sr_/g' | sed 's/^/sr_/'| sed 's+/+ remove +g' | sh -x

echo "hoho 1"

echo $flow_confs |  sed 's/ / ; rm sr_/g' | sed 's/^/rm sr_/' | sed 's+/+_+g' | sed 's/\.conf/_000?.log/g' | (cd $LOGDIR; sh -x )

echo $flow_confs |  sed 's/ / ; rm /g' | sed 's/^/rm /' | sed 's+\.conf+/*+g' | (cd $CACHEDIR; sh -x)

rm $LOGDIR/sr_audit* $LOGDIR/sr_poll_pulse*

httpdr=""
if [ -f .httpdocroot ]; then
   httpdr="`cat .httpdocroot`"
   if [ "$httpdr" ]; then
      rm -rf $httpdr
   fi
fi

