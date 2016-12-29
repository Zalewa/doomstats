#!/bin/bash
#
# They told me about using automatic deployment tools
# such as 'fabric'... BUT I DIDN'T LISTEN!
#

# Preparatory steps. Spawn new directory in temp space.
set -e

scriptdir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
workdir=`pwd`
builddir=`mktemp -d`/doomstats

# Go to the directory where this script is located and get
# the commit hash of the current HEAD.
cd $scriptdir
githash=`git log -n 1 --format=format:%h`

# Export current HEAD to the build directory.
mkdir -p $builddir
git worktree add "$builddir" HEAD

# Go to the build directory and build.
cd $builddir
rm .git
rm .gitignore
python ./manage.py collectstatic --noinput
sed -i -r 's/^DEBUG\s*=.*True$/DEBUG = False/' $builddir/doomstats/settings.py
sed -i -r 's/^ALLOWED_HOSTS\s*=.*$/ALLOWED_HOSTS = ["*"]/' $builddir/doomstats/settings.py
pyclean -v .
cd ..

# Package the build.
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
