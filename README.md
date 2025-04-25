## Tasks
- Oracle cloud: docker-test & ghcr 배포
  - docker run -p 8080:8080 -v $(pwd):/app ical-service
  - docker run -d --name fastapi-https -p 443:443 -v /etc/letsencrypt:/etc/letsencrypt:ro -v $(pwd):/app ical-service