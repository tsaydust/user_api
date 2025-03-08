from datetime import timedelta

JWT_SECRET_KEY = "kuawbdbkauwdlkoiahwd"
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=20)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=15)

ALIYUN_OSS_ENDPOINT = "https://oss-cn-hangzhou.aliyuncs.com"
ALIYUN_OSS_BUCKET = "sec-kill"
ALIYUN_OSS_REGION = "cn-hangzhou"
ALIYUN_OSS_DOMAIN = "https://sec-kill.oss-cn-hangzhou.aliyuncs.com/"

CONSUL_HOST = '127.0.0.1'
CONSUL_HTTP_PORT = 8500
# user_service.service.consul
CONSUL_DNS_PORT = 8600

SERVER_PORT = 8000