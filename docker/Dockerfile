FROM python:3.12-bookworm
RUN apt-get update \
    && apt-get install -y dumb-init curl git build-essential
RUN bash -c "$(curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh)" \
	&& bash -l -c "nvm install 20"
EXPOSE 3000
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["bash"]
