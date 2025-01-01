# Containers

## Pre-requisites:
The containers will need to be built and uploaded to a REPO server within your control. These containers do
not exist on any public repo.

### Add local repo into Docker
Add Harbor to Docker's daemon configuration (/etc/docker/daemon.json on Linux):
```
{
  "insecure-registries": ["harbor.domain.name.com"]
}
```
Restart Docker after making this change:
```
sudo systemctl restart docker
```

### Build the images
Assuming you are in the directory containing your Dockerfile, run the following command to build the Docker image and assign it a name:
```
docker build -t myImage:latest .
```

Tag the Image for Harbor
```
docker tag myImage:latest harbor.DOMAIN.NAME.COM/myproject/myImage:latest
```

Push the Image
```
docker push harbor.DOMAIN.NAME.COM/myproject/myImage:latest