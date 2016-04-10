FROM komand/python-plugin 

ADD ./plugin.spec.yaml /plugin.spec.yaml
ADD . /python/src/foobar

WORKDIR /python/src/foobar
RUN make plugin

ENTRYPOINT ["/usr/local/bin/foobar"]
