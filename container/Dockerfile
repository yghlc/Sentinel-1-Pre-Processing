FROM ubuntu:22.04

# Install base utilities
RUN apt-get update && apt-get install -y  \
        build-essential \
        pkg-config \
        zip \
        unzip \
        git \
	    wget \
	    && \
        apt-get clean && \
        rm -rf /var/lib/apt/lists/*

# Install miniconda
ENV CONDA_DIR /opt/miniconda3
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/sh ~/miniconda.sh -b -p /opt/miniconda3  && rm ~/miniconda.sh

# Make RUN commands use the new environment (conda base): 
SHELL ["conda", "run", "-n", "base", "/bin/bash", "-c"]

# Put conda in path so we can use conda activate
ENV PATH=$CONDA_DIR/bin:$PATH

# install python package
RUN conda install -c conda-forge -y asf_search
RUN conda install -c conda-forge -y geopandas
## this will also install GDAL
RUN conda install -c conda-forge -y rasterio

RUN pip install elevation

# t: tarball, i index-cache p: package  y: Do not ask for confirmation
RUN conda clean -tipy

# install SNAP
RUN wget --quiet https://download.esa.int/step/snap/9.0/installers/esa-snap_all_unix_9_0_0.sh -O ~/esa-snap.sh && \
    /bin/sh ~/esa-snap.sh -q -dir /opt/snap  && rm ~/esa-snap.sh

# update SNAP when a container launch?
#RUN /opt/snap/bin/snap --nosplash --nogui --modules --update-all

# clone github repo
RUN git clone https://github.com/yghlc/Sentinel-1-Pre-Processing.git /opt/Sentinel-1-Pre-Processing

# set some environment
ENV PATH=/opt/Sentinel-1-Pre-Processing:$PATH
ENV SNAP_BIN_GPT=/opt/snap/bin/gpt
ENV GDAL_TRANSLATE_BIN=/opt/miniconda3/bin/gdal_translate

COPY run.sh .
# WORKDIR /data

CMD ["conda", "run", "--no-capture-output", "-n", "base","/bin/bash","-c","./run.sh"]

