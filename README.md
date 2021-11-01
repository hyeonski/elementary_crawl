# elementary_crawl

초등학교의 공지사항, 가정통신문, 급식 소식을 크롤링하는 프로젝트입니다.



## DB

MySQL 데이터베이스를 Docker-compose를 통해 빌드합니다.

#### Requirements

- Docker (Docker-compose)

#### Run

```
./run.sh
```



## Crawler

#### Requirements

- Python 3.6+
- Google Cloud Storage Bucket
- 나이스 교육정보 개방 포털 Open API 인증키 ([인증키 발급](https://open.neis.go.kr/portal/guide/actKeyPage.do))

#### Setting

1. Google Cloud Storage 접큰 키를 google_credentials.json로 저장합니다.
2. .env를 작성합니다. (.env.sample 참고)

#### Run

```
python3 -m venv .venv
./run.sh
```



## Server

NestJS + Handlebars로 작성된 크롤링 데이터 확인 애플리케이션입니다.

#### Requirements

- Node.js

#### Setting

.env를 작성합니다. (.env.sample 참고)

#### Run

```
npm install
npm run start
```

