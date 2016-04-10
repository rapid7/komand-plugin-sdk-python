FROM golang:1.5

ENV GO15VENDOREXPERIMENT=1

# dependencies 
RUN go get github.com/jteeuwen/go-bindata/...
RUN go get github.com/golang/lint/golint 
RUN go get github.com/tools/godep

# gometalinter
RUN go get github.com/alecthomas/gometalinter
RUN gometalinter --install

VOLUME /go/src/komand
WORKDIR /go/src/komand
ENV BASE=/go/src/komand
