#!/bin/bash
#
# They told me about using automatic deployment tools
# such as 'fabric'... BUT I DIDN'T LISTEN!

set -e

scriptdir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
workdir=`pwd`
tmpname=`uuidgen`
builddir=/tmp/$tmpname/doomstats

mkdir -p $builddir
cp -R $scriptdir/* $builddir
cp -R $scriptdir/.git $builddir

cd $builddir
git clean -fd
githash=`git log -n 1 --format=format:%h`
rm -rf $builddir/.git
python ./manage.py collectstatic --noinput
sed -i -r 's/^DEBUG\s*=.*True$/DEBUG = False/' $builddir/doomstats/settings.py
sed -i -r 's/^ALLOWED_HOSTS\s*=.*$/ALLOWED_HOSTS = ["*"]/' $builddir/doomstats/settings.py
cd ..

stamp=`date +%Y%m%d-%H%M%S`
tar -cvzf "$workdir/doomstats-$stamp-$githash.tar.gz" ./doomstats

exit 0

#               ,
#              ```.
#            ;':```:';';
#          ,;;::````:::''''':
#          ':::'.```';;':::::::',
#          ':';;.``';;:::;;;;;;;;';
#          '::,.,``';:::;;;;;;;;;;;',``,
#          '````,`.':::';;;;;;;;;;,````,
#        ,.,````````;::;;;'+;;'+',```````
#       ,+```````````':;'```````:`````..
#      , ``````````,' `.  .+`````````.`,
#       :``````````         @`````````.::;;'
#    ,,``````````      :#   @``````.``::::'
# ,.````````````       .+;, .`````.`.;;'''
#  .````````````          `.```````,;;;;,
#  ,```````````.``.:`   .+```````,';;;'
#     .,:,,,,. :`````..```````````,;''
#     .``````,',``````````````````.:;'
#        `;;;',````````````````````,;,
#        ,';;,``````````````````````,:
#        ,;;,`````````````,``````````,
#        :,```````..,:,.``````````````.
#        .,.``,.      ,````````````
#                      ,```````
#                      ,```
#
