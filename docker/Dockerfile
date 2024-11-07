FROM python:3

RUN python3 -m pip install --no-cache-dir -U ladok3 && \
  ln -f $(find / -name ladok.bash) /etc/bash_completion.d
