FROM mysterysd/wzmlx:latest
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip3 install --upgrade setuptools wheel && \
    pip3 install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x ./aria.sh
RUN chmod -R 777 .
ENV XDG_CACHE_HOME=/usr/src/app/.cache
ENV HOME=/usr/src/app
CMD ["bash", "start.sh"]