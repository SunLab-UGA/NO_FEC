# NO_FEC
This is an exploration of a GNU_Radio 802.11 without Forward Error Correction

## install instructions
* install radioconda and mamba
    * https://github.com/ryanvolz/radioconda
* create a new env (no_fec)
```
conda create -n no_fec 
```
* install gnuradio and dependencies
```
mamba install gnuradio gnuradio-build-deps boost
```
* reopen env
```
conda activate no_fec
```
* build/install gr-foo (gr-foo-maint-3.10)
### build/install commands
```
mkdir build
cd build
cmake -G Ninja -DCMAKE_INSTALL_PREFIX=$CONDA_PREFIX -DCMAKE_PREFIX_PATH=$CONDA_PREFIX -DLIB_SUFFIX="" ..
cmake --build .
cmake --build . --target install
```
* build/install NO-FEC (gr-ieee802-11-maint-3.10_NO-FEC)
    *same build/install steps as above



