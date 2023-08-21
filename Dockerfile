FROM    debian
ARG     DEBIAN_FRONTEND=noninteractive

RUN     apt-get update
RUN     apt-get install -y mumble-server # mumble-server
RUN     apt-get install -y python3 python3-dev python3-pip gcc g++ libssl-dev libbz2-dev # zeroc-ice and project dependencies

RUN     mkdir -p /mumble
WORKDIR /mumble

ADD     requirements.txt .
RUN     pip3 install -r requirements.txt --break-system-packages

ADD     . .

EXPOSE  64738 751 80
ENTRYPOINT ["sh", "entrypoint.sh"]