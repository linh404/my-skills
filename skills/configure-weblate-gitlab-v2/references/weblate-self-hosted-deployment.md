# Cấu hình Weblate Self-host

## Mục lục

1. Phạm vi
2. Mô hình triển khai
3. Yêu cầu trước khi triển khai
4. Cấu trúc thư mục khuyến nghị
5. Cấu hình environment
6. Docker Compose
7. HTTPS, tunnel và reverse proxy
8. Machine translation service tùy chọn
9. Khởi động và kiểm tra hạ tầng
10. Hardening sau proof of concept
11. Lỗi thường gặp
12. Tài liệu tham chiếu

## 1. Phạm vi

Tài liệu này mô tả cách triển khai và vận hành instance Weblate self-host bằng Docker Compose cho pilot tích hợp Odoo QMS.

Tài liệu chỉ tập trung vào lớp hạ tầng:

- Weblate application.
- PostgreSQL.
- Valkey/Redis dùng cho cache và task queue.
- HTTPS, tunnel hoặc reverse proxy.
- Persistent volumes và secret.
- Kết nối mạng từ container Weblate tới GitLab.

Các nội dung sau không thuộc tài liệu này:

- Cấu hình project, component và file trên Weblate: xem `weblate-settings-configuration.md`.
- Token, webhook, branch và quyền GitLab: xem `weblate-gitlab-integration.md`.
- CI job export POT: tài liệu CI job hiện có.
- Kiến trúc tổng thể: plan architect hiện có.

## 2. Mô hình triển khai

### 2.1. Thành phần bắt buộc

| Thành phần | Vai trò |
|---|---|
| Weblate | Giao diện dịch, quản lý component, commit PO và gọi GitLab API khi tạo MR |
| PostgreSQL | Lưu project, component, user, translation state và lịch sử Weblate |
| Valkey | Cache, task queue và các tác vụ nền; service hiện tại dùng `valkey/valkey:9.1.1` |
| HTTPS endpoint | Cho người dùng truy cập và để GitLab gửi webhook |

### 2.2. Thành phần tùy chọn

| Thành phần | Vai trò | Điều kiện sử dụng |
|---|---|---|
| LibreTranslate | Cung cấp machine-translation suggestion nội bộ | Cần bản dịch nháp hoặc proof of concept không gửi dữ liệu ra ngoài |
| Ollama hoặc engine khác | Cung cấp suggestion nội bộ | Chỉ bật khi đã kiểm tra tài nguyên và chất lượng đầu ra |

Machine translation không phải điều kiện bắt buộc để Weblate đồng bộ POT/PO hoặc tạo GitLab MR.

## 3. Yêu cầu trước khi triển khai

- Docker Engine và Docker Compose plugin.
- Một hostname HTTPS ổn định cho Weblate.
- DNS hoặc tunnel/reverse proxy trỏ được tới Weblate.
- GitLab có thể được truy cập từ bên ngoài đối với webhook, hoặc có cơ chế route phù hợp.
- Container Weblate có thể truy cập GitLab qua mạng công ty/VPN đối với các thao tác Git và API.
- Dung lượng persistent volume cho PostgreSQL, Weblate data và cache.
- Không lưu token, password thật trong repository hoặc file Compose được commit.

Tunnel chỉ giải quyết chiều truy cập vào Weblate. Tunnel không tự động chuyển lưu lượng outbound từ container Weblate tới GitLab qua VPN.

### 3.1. Baseline đang chạy

Môi trường proof of concept hiện tại gồm:

| Service | Image/runtime | Cấu hình đáng chú ý |
|---|---|---|
| `cache` | `valkey/valkey:9.1.1` | Persistent volume `redis-data`, snapshot mỗi 60 giây, `read_only` |
| `database` | `postgres:18-alpine` | Persistent volume `postgres-data` tại `/var/lib/postgresql` |
| `weblate` | `weblate/weblate` | Đọc `./environment`, expose `80:8080`, `read_only`, dùng `/run` và `/tmp` là `tmpfs` |
| `ollama` | `ollama/ollama:latest` | Persistent volume `ollama-data`; service MT/LLM tùy chọn |

Compose hiện tại dùng file `./environment` thông qua `env_file`. File này được dùng chung bởi `weblate` và `database`; các biến GitLab trong đó chỉ có ý nghĩa đối với Weblate.

## 4. Cấu trúc thư mục khuyến nghị

```text
weblate/
├── compose.yml
├── environment
└── data/
```

File `environment` chứa giá trị thật phải nằm ngoài Git hoặc được đưa vào `.gitignore`. Với môi trường production, nên tách secret thành Docker secrets hoặc secret store của hệ thống triển khai.

## 5. Cấu hình environment

File `environment` được nạp bằng `env_file`, vì vậy phải sử dụng cú pháp `KEY=value`. Không dùng cú pháp YAML `KEY: value` trong file này.

Ví dụ giá trị đã được loại bỏ secret:

```dotenv
WEBLATE_DEBUG=0
WEBLATE_LOGLEVEL=INFO
WEBLATE_SITE_DOMAIN=<current-quick-tunnel-hostname>
WEBLATE_ALLOWED_HOSTS=*
WEBLATE_ENABLE_HTTPS=1
WEBLATE_SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
WEBLATE_IP_PROXY_HEADER=HTTP_X_FORWARDED_FOR

WEBLATE_ADMIN_NAME=Weblate Admin
WEBLATE_ADMIN_EMAIL=admin@example.com
WEBLATE_ADMIN_PASSWORD=<temporary-password-only>

POSTGRES_PASSWORD=<database-password>
POSTGRES_USER=weblate
POSTGRES_DB=weblate
POSTGRES_HOST=database
POSTGRES_PORT=5432

REDIS_HOST=cache
REDIS_PORT=6379

CLIENT_MAX_BODY_SIZE=1000M

WEBLATE_SERVER_EMAIL=admin@example.com
WEBLATE_DEFAULT_FROM_EMAIL=weblate@example.com
```

Quy tắc:

- `WEBLATE_SITE_DOMAIN` chỉ chứa hostname, không thêm `https://`.
- `WEBLATE_ALLOWED_HOSTS` phải khớp hostname thực tế.
- HTTPS thường được terminate ở tunnel hoặc reverse proxy; Weblate vẫn cần nhận đúng forwarded headers.
- Không để `WEBLATE_ADMIN_PASSWORD` dạng plain text trong environment lâu dài sau khi tạo administrator ban đầu.
- Không cấu hình đồng thời biến token dạng giá trị và biến token dạng `_FILE` cho cùng một secret.

Credential dùng để GitLab clone/push hoặc tạo MR được cấu hình trong tài liệu GitLab integration, không lặp lại ở đây.

Giữ `POSTGRES_DB` là biến chính cho PostgreSQL. Chỉ giữ alias `POSTGRES_DATABASE` nếu stack Weblate cũ đang thực sự yêu cầu biến này; không thêm cả hai để che giấu cấu hình không nhất quán.

Các setting `WEBLATE_ALLOWED_HOSTS=*`, mở đăng ký và tắt CAPTCHA chỉ phù hợp với proof of concept. Không giữ nguyên các setting này khi public instance được dùng cho dữ liệu thật.

## 6. Docker Compose

Compose thực tế có bốn service: Weblate, PostgreSQL, Valkey và Ollama. Weblate Docker dùng PostgreSQL và Valkey làm các thành phần chính; Ollama chỉ là service tùy chọn cho machine-translation/LLM suggestion. Tên image và version cần được pin theo phiên bản đã kiểm thử; hiện `weblate/weblate` và `ollama/ollama:latest` vẫn chưa pin version.

Compose baseline đã loại bỏ secret:

```yaml
  cache:
    image: valkey/valkey:9.1.1
    volumes:
      - redis-data:/data
    command: [valkey-server, --save, '60', '1', --loglevel, warning]
    restart: always
    read_only: true

  database:
    image: postgres:18-alpine
    volumes:
      - postgres-data:/var/lib/postgresql
    env_file:
      - ./environment
    restart: always

  weblate:
    image: weblate/weblate
    depends_on:
      - cache
      - database
    volumes:
      - weblate-data:/app/data
      - weblate-cache:/app/cache
    env_file:
      - ./environment
    ports:
      - "80:8080"
    restart: always
    read_only: true
    tmpfs:
      - /run
      - /tmp

  ollama:
    image: ollama/ollama:latest
    restart: unless-stopped
    volumes:
      - ollama-data:/root/.ollama

volumes:
  weblate-cache: {}
  weblate-data:
  postgres-data:
  redis-data:
  ollama-data:
```

PostgreSQL 18 dùng `/var/lib/postgresql` làm mount target mặc định mới. Không đổi về `/var/lib/postgresql/data` nếu chưa đặt `PGDATA` tương ứng; nếu không, dữ liệu có thể nằm ngoài persistent volume.

## 7. HTTPS, tunnel và reverse proxy

### 7.1. Proof of concept

Có thể sử dụng tunnel tạm thời để kiểm thử:

- Tunnel phải chuyển request HTTPS tới cổng Weblate.
- Hostname của tunnel phải được khai báo trong `WEBLATE_SITE_DOMAIN` và `WEBLATE_ALLOWED_HOSTS`.
- URL webhook GitLab phải dùng đúng hostname hiện tại.
- Khi hostname thay đổi, phải cập nhật lại environment và webhook.

Quick tunnel phù hợp cho proof of concept, không phù hợp làm endpoint production vì hostname có thể thay đổi và làm hỏng webhook.

### 7.2. Môi trường ổn định

Production nên sử dụng hostname cố định, TLS hợp lệ và reverse proxy có các đặc tính:

- Forward đúng `Host`.
- Forward `X-Forwarded-Proto=https`.
- Không chặn request webhook.
- Có giới hạn upload phù hợp với file dịch.
- Có timeout đủ dài cho tác vụ Weblate.

## 8. Machine translation service tùy chọn

Nếu chọn LibreTranslate nội bộ, chạy service riêng trong cùng Docker network với Weblate:

```yaml
services:
  libretranslate:
    image: libretranslate/libretranslate:<tested-version>
    restart: unless-stopped
    environment:
      LT_UPDATE_MODELS: "true"
      LT_LOAD_ONLY: "en,vi"
    volumes:
      - libretranslate-models:/home/libretranslate/.local

volumes:
  libretranslate-models:
```

Weblate sẽ truy cập service qua hostname nội bộ, ví dụ `http://libretranslate:5000/`; không cần mở port service ra Internet nếu chỉ Weblate sử dụng.

Ollama trong baseline hiện tại cũng chỉ là container runtime. Việc container đang chạy không đồng nghĩa Weblate đã sử dụng Ollama; provider và thao tác dịch phải được cấu hình, kiểm thử trong Weblate Settings riêng.

Việc bật provider trong giao diện Weblate được mô tả ở `weblate-settings-configuration.md`.

## 9. Khởi động và kiểm tra hạ tầng

```bash
docker compose config
docker compose up -d
docker compose ps
docker compose logs --tail=100 weblate
```

Kiểm tra tối thiểu:

1. Các container Weblate, PostgreSQL và cache ở trạng thái healthy hoặc running ổn định.
2. URL HTTPS mở được mà không bị redirect loop hoặc lỗi CSRF.
3. Weblate tạo link theo hostname HTTPS đã cấu hình.
4. Weblate kết nối được PostgreSQL và cache.
5. Container Weblate phân giải được hostname GitLab.
6. Endpoint `/hooks/gitlab/` truy cập được từ GitLab.
7. Persistent data vẫn còn sau khi recreate container.

Sau khi thay đổi environment:

```bash
docker compose up -d --force-recreate weblate
docker compose ps
docker compose logs --tail=100 weblate
```

## 10. Hardening sau proof of concept

Trước khi dùng ngoài môi trường thử nghiệm:

- Đóng đăng ký tự do nếu không cần thiết.
- Không dùng wildcard host.
- Đổi password administrator tạm thời.
- Tắt dummy email backend nếu cần gửi thông báo thật và đã có SMTP an toàn.
- Pin version image.
- Backup PostgreSQL và Weblate data.
- Giới hạn quyền của user vận hành và container.
- Kiểm tra log không chứa token hoặc password.
- Dùng hostname HTTPS cố định.

## 11. Lỗi thường gặp

### 11.1. Environment và container

| Hiện tượng | Nguyên nhân | Cách kiểm tra và xử lý |
|---|---|---|
| Biến cấu hình không có hiệu lực | File `./environment` dùng `KEY: value` thay vì `KEY=value` | Chuyển toàn bộ file về cú pháp env file; chạy `docker compose config`; recreate container |
| Đổi environment nhưng Weblate vẫn dùng giá trị cũ | Restart không tạo lại container | Chạy `docker compose up -d --force-recreate weblate` rồi kiểm tra log |
| Weblate không khởi động | Sai biến database/cache, quyền volume hoặc lỗi migration | Chạy `docker compose ps`, `docker compose logs --tail=100 weblate` và kiểm tra `database`/`cache` trước |
| Weblate lỗi ghi file khi bật `read_only` | Đường dẫn ghi chưa được mount hoặc thiếu `tmpfs` | Giữ volume `/app/data`, `/app/cache` và `tmpfs` `/run`, `/tmp`; không tắt `read_only` để che giấu lỗi |
| `docker compose config` báo lỗi | Compose YAML sai indentation, volume hoặc env_file path | Kiểm tra file được tham chiếu tương đối từ thư mục chứa `compose.yml` |

### 11.2. HTTPS và tunnel

| Hiện tượng | Nguyên nhân | Cách kiểm tra và xử lý |
|---|---|---|
| Redirect loop hoặc lỗi CSRF | Domain, HTTPS flag hoặc forwarded header không khớp | Kiểm tra `WEBLATE_SITE_DOMAIN`, `WEBLATE_ENABLE_HTTPS`, `WEBLATE_SECURE_PROXY_SSL_HEADER` và `WEBLATE_IP_PROXY_HEADER` |
| Link Weblate sinh ra dùng HTTP | Weblate không nhận biết HTTPS terminate ở tunnel/reverse proxy | Forward `X-Forwarded-Proto: https` và recreate Weblate |
| Webhook đang chạy thì mất tác dụng | Quick tunnel đổi hostname | Cập nhật `WEBLATE_SITE_DOMAIN`, `WEBLATE_ALLOWED_HOSTS` và URL webhook; quick tunnel chỉ dùng cho proof of concept |
| GitLab gọi webhook thất bại | Endpoint không public, TLS/tunnel/firewall lỗi | Test URL `/hooks/gitlab/` từ bên ngoài và xem webhook request history của GitLab |

### 11.3. Database, cache và persistent volume

| Hiện tượng | Nguyên nhân | Cách kiểm tra và xử lý |
|---|---|---|
| Weblate không kết nối database | Dùng sai hostname; trong Compose phải dùng `database`, không dùng `localhost` | Kiểm tra `POSTGRES_HOST=database`, `POSTGRES_PORT=5432` và log hai service |
| Mất database sau recreate | Volume không được mount hoặc mount sai đường dẫn | Kiểm tra volume `postgres-data`; PostgreSQL 18 dùng `/var/lib/postgresql` |
| PostgreSQL 18 ghi dữ liệu ngoài volume | Dùng mount cũ `/var/lib/postgresql/data` mà không đặt `PGDATA` | Giữ mount `/var/lib/postgresql` như baseline hoặc cấu hình `PGDATA` nhất quán |
| Đổi `POSTGRES_PASSWORD` làm Weblate mất kết nối | Password trong environment không tự đổi password của role đã tồn tại | Đổi password role trong PostgreSQL trước, sau đó cập nhật environment và recreate Weblate |
| Cache không hoạt động | Sai service name, cache container dừng hoặc volume/runtime lỗi | Kiểm tra `REDIS_HOST=cache`, port 6379 và `docker compose logs cache` |

### 11.4. GitLab và machine translation từ container

| Hiện tượng | Nguyên nhân | Cách kiểm tra và xử lý |
|---|---|---|
| Host truy cập GitLab nhưng Weblate không truy cập được | Tunnel vào Weblate không cung cấp route outbound tới GitLab VPN | Kiểm tra DNS/HTTPS từ chính container Weblate; kiểm tra VPN và firewall của host |
| LibreTranslate không kết nối | Service khác Docker network, sai hostname hoặc chưa listen port 5000 | Dùng hostname nội bộ `libretranslate`, kiểm tra `docker compose ps` và log service |
| Ollama chạy nhưng Weblate không có suggestion | Container Ollama không tự đăng ký thành provider Weblate | Cấu hình provider trong Weblate Settings và test một source unit |
| Credential xuất hiện trong log hoặc file commit | Secret đặt trực tiếp trong Compose/environment được commit | Revoke/rotate credential, thay bằng secret store hoặc file bảo vệ; không sao chép secret vào tài liệu |

## 12. Tài liệu tham chiếu

- [Weblate Docker documentation](https://docs.weblate.org/en/latest/admin/install/docker.html)
- [Weblate configuration](https://docs.weblate.org/en/latest/admin/config.html)
- [Docker Compose documentation](https://docs.docker.com/compose/)
