# install instructions from freshly installed OS (ubuntu 22.04)
* general overview
  * install radioconda
  * create new conda env
  * install gnuradio and dependencies
  * build/install a foo library (a submodule for 802_11) **into the conda env**
  * build/install the no_fec mod **also into the conda env**

# download radioconda from
[radioconda](https://github.com/ryanvolz/radioconda/releases/)
# edit permissions and install
(conda is now installed)

# deactivate base env (good practice)
conda deactivate

# disable automatically loading the base env (not required but good practice)
conda config --set auto_activate_base false

# make a new env
conda create -n nofec

# activate the new env
conda activate nofec

# install gnuradio and dependencies (make sure to run "sudo apt update" beforehand)
(mamba is a conda installer which is just better...)
mamba install gnuradio gnuradio-build-deps boost

# add fireware files
sudo apt install uhd-host
uhd_images_downloader

# create USB rules (link them?)
sudo ln -s $CONDA_PREFIX/lib/uhd/utils/uhd-usrp.rules /etc/udev/rules.d/radioconda-uhd-usrp.rules
sudo udevadm control --reload
sudo udevadm trigger

# run volk_profile (used to optimize cpu instructions for gnu-radio)
cd /bin
volk_profile

# ensure in conda env, and navagate to NO_FEC folder

# first build the foo modules, remove any previous build folders
* follow the build and install code below, **this installs into the conda env**
# then, build the 802_11 modules (no_fec or symbol_mod)

```
mkdir build
cd build
cmake -G Ninja -DCMAKE_INSTALL_PREFIX=$CONDA_PREFIX -DCMAKE_PREFIX_PATH=$CONDA_PREFIX -DLIB_SUFFIX="" ..
cmake --build .
cmake --build . --target install
```

# open gnuradio_companion
gnuradio_companion

# open the wifi_phy_FEC_disable.grc and hit play to load the hier block

# congrats! you've installed gnuradio, compiled, and installed your first modules!
