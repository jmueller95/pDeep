FROM tensorflow/tensorflow:1.14.0-py3
RUN pip install keras flask
ENV KERAS_BACKEND=tensorflow
ENV TF_CPP_MIN_LOG_LEVEL=3
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

ADD pDeep2/ /root/pDeep2
RUN cd /root/
WORKDIR /root/
