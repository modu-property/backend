# Used
* jwt
* serializer
* postgresql
* sqlite
* form
* celery
* redis
* pytest
* pytest-xdist
* docker-compose

# pycharm setting
run server
![img.png](z_images_for_readme/img.png)
run celery
![img_1.png](z_images_for_readme/img_1.png)
run celery task

![img_2.png](z_images_for_readme/img_2.png)

result
![img_3.png](z_images_for_readme/img_3.png)

celery 사용법
* celery beat 실행해서 redis 큐에 주기적으로 task 넣기
* celery worker 실행해서 redis 큐에 있는 task 실행

# pytest
pytest
pytest -n {n}

# docker-compose
docker-compose -f docker-compose.local.yml up -d --build

docker-compose -f docker-compose.dev.yml up -d --build

# lightsail 인스턴스에 key 설정하기
* 인스턴스에 ssh 접속
* key 생성 : ssh-keygen -t ed25519 -a 200 -C "samnaka@naver.com"
* ~/.ssh/authorized_keys 파일에 새로 만든 id_ed25519.pub 값 이어 붙여주기. `cat id_ed25519.pub >> authorized_keys`
* github 사이트에서 profile -> setting -> ssh and gpg keys 에도 id_ed25519.pub 등록해야 함
* SSH_PRIVATE_KEY_DEV 키는 id_ed25519(개인키) 넣어줘야 함
* key 줄바꿈 안되면 엔터 쳐서 이런 모양 만들어야함.
```
-----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----
```

sudo vi /etc/ssh/sshd_config
PasswordAuthentication no -> PasswordAuthentication yes 로 수정
PubkeyAcceptedKeyTypes=+ssh-rsa 추가
