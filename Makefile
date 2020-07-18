IMAGE = pdeep2
DOCKERFILE = Dockerfile
HOSTPORT = 5050

build:
	docker build -qf $(DOCKERFILE) -t $(IMAGE) .

server: build
	docker run -it -v "$(TF_MODELS)":/root/tf-models/ -p $(HOSTPORT):$(HOSTPORT) $(IMAGE) python3 -m pDeep2.server -p $(HOSTPORT)
