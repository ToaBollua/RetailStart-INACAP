FROM alpine:latest
RUN apk add --no-cache bash tar
WORKDIR /scripts
COPY backup.sh .
RUN chmod +x backup.sh
CMD ["./backup.sh"]
