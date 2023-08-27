FROM    debian
ARG     DEBIAN_FRONTEND=noninteractive

RUN     apt-get update
RUN     apt-get install -y mumble-server # mumble-server
RUN     apt-get install -y python3 python3-zeroc-ice # projects dependencies

RUN     mkdir -p /mumble
WORKDIR /mumble

ADD     . .

EXPOSE  64738 751 80
ENTRYPOINT ["sh", "entrypoint.sh"]
