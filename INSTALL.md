
The main steps to get to a SPQReL workspace:

1. Make sure you have at least these things installed (based on Ubuntu Xenial amd64):

    ```
    sudo apt-get update
    sudo apt-get -y --force-yes upgrade
    sudo apt-get install -y --force-yes \
						curl autoconf make cmake python python-pip zip \
						git build-essential gcc-multilib g++-multilib flex bison \
						libboost-dev libboost-regex-dev libxml2-dev libxml++2.6-dev \
						vim nano libpng12-dev libfl-dev
    sudo pip install --upgrade pip
    sudo pip install qibuild tmule
    ```

1. create your top-level workspace, we assume `$HOME/spqrel` for now, you may chose something else.

    ```
    mkdir -p $HOME/spqrel/workspace
    ```

1. download and install the SDK:

   ```
   cd $HOME/spqrel
   # download cross compilation toolchain (optional)
   curl https://lcas.lincoln.ac.uk/owncloud/index.php/s/prwtrlDAsdagt1h/download > /ctc-linux64-atom-2.5.2.74.zip && \
		unzip /ctc-linux64-atom-2.5.2.74.zip && \
		rm /ctc-linux64-atom-2.5.2.74.zip
   # download Python SDK
   curl https://lcas.lincoln.ac.uk/owncloud/index.php/s/424z8mYr9TKX7J7/download | tar xz
   # download main NaoQi SDK
   curl https://lcas.lincoln.ac.uk/owncloud/index.php/s/1PLbRNtgklY6NCB/download | tar xz

   cd $HOME/spqrel/workspace
   # Main development SDK, called linux64
   qitoolchain create linux64 ../naoqi-sdk-2.5.5.5-linux64/toolchain.xml
   qibuild add-config linux64 -t linux64
   
   # cross-compilation toolchain for Pepper (optional)
   qitoolchain create pepper ../ctc-linux64-atom-2.5.2.74/toolchain.xml
   qibuild add-config pepper -t pepper
   ```

