FROM postgres:12


RUN apt-get update && apt-get install -y awscli

RUN mkdir -p /data_dumps/
WORKDIR /data_dumps

ADD getS3DataDump.sh /data_dumps/getS3DataDump.sh
RUN chmod 777 /data_dumps/getS3DataDump.sh
RUN chmod ugo+rwx /data_dumps/
