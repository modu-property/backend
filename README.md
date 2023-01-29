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
