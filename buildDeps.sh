#!/usr/bin/env bash
set -e

if [ -d ./thirdparty ]; then
	rm -rf ./thirdparty
fi

mkdir -p ./thirdparty
cd ./thirdparty

mkdir -p ./build/share
cat << EOF > ./build/share/config.site
CPPFLAGS='-I`pwd`/build/include -fPIC'
LDFLAGS=-L`pwd`/build/lib
EOF

# cfitsio

curl -L http://heasarc.gsfc.nasa.gov/FTP/software/fitsio/c/cfitsio-3.48.tar.gz -o cfitsio.tar.gz
tar -xzf cfitsio.tar.gz
rm cfitsio.tar.gz

cd cfitsio-3.48
./configure --prefix=`pwd`/../build --disable-curl
make install -j 4

cd ..

# CCFits

curl -L https://heasarc.gsfc.nasa.gov/fitsio/CCfits/CCfits-2.5.tar.gz -o CCfits.tar.gz
tar -xzf CCfits.tar.gz
rm CCfits.tar.gz

cd CCfits
./configure --prefix=`pwd`/../build --enable-static=yes --enable-shared=no
make install -j 4
