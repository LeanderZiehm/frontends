podman-run:
	podman build --cgroup-manager cgroupfs -t frontends . && podman run --rm -it -v ssh_data:/app/data -p 8100:8100 frontends

docker-run:
	docker build -t frontends . && docker run --rm -it -v ssh_data:/app/data -p 8100:8100 frontends