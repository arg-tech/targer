# Use an official Python 3.5 64-bit runtime as a parent image
FROM python:3.5

# Add all Data
ADD . /

# Set the working directory to /
WORKDIR /




# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt
RUN pip install torch==0.4.1 -f https://download.pytorch.org/whl/torch_stable.html
RUN pip install torchvision==0.2.1 -f https://download.pytorch.org/whl/torch_stable.html

RUN git clone https://github.com/UKPLab/emnlp2017-bilstm-cnn-crf.git

RUN mv backend.py emnlp2017-bilstm-cnn-crf/ && mv Model.py emnlp2017-bilstm-cnn-crf/ && mv ModelNewES.py emnlp2017-bilstm-cnn-crf/ && mv ModelNewWD.py emnlp2017-bilstm-cnn-crf/ && mv Segmenter.py emnlp2017-bilstm-cnn-crf/ && mv data.py emnlp2017-bilstm-cnn-crf/ && mv main.py emnlp2017-bilstm-cnn-crf/

RUN mv models/* emnlp2017-bilstm-cnn-crf/models/

RUN mv -f BiLSTM.py emnlp2017-bilstm-cnn-crf/neuralnets/

RUN mkdir emnlp2017-bilstm-cnn-crf/lstm

RUN git clone https://github.com/achernodub/bilstm-cnn-crf-tagger.git emnlp2017-bilstm-cnn-crf/lstm

# Make port 6000 available to the world outside this container
EXPOSE 6000

WORKDIR /emnlp2017-bilstm-cnn-crf

# Run app.py when the container launches
CMD ["python3", "main.py"]

