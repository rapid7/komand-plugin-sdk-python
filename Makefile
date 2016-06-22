
.PHONY: all

all: 
	make -C python image  
	make -C go image
