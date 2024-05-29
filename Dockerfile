FROM python:3.11-alpine

# Install updates
RUN apk update

# Install updates
RUN apk add bash pipx

# Copy the current directory contents into the container at /app
COPY . /app
WORKDIR /app

# Setup pipx
RUN pipx ensurepath
RUN pipx completions
RUN echo "eval \"\$(register-python-argcomplete pipx)\"" >> ~/.bashrc
RUN pipx install .

ENTRYPOINT ["/root/.local/bin/nmapSubnetOnline"]