FROM python:3.8

RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential make git g++ gcc gfortran \
  sqlite3 libgdal-dev python3-gdal gdal-bin \
  libspatialindex-dev python-rtree \
  && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/OSGeo/proj.4.git \
  &&    cd proj.4 \
  &&    ./autogen.sh \
  && ./configure --prefix=/usr \
  --mandir=/usr/share/man \
  && make -j 4 \
  && make install

RUN pip install --upgrade pip && \
  pip install Cython numpy scipy pandas convertdate lunarcalendar h5py && \
  rm -fr /root/.cache

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "./forecast.py"]