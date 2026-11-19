FROM python:3.11-slim-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends --only-upgrade perl-base \
    && perl_base_version="$(dpkg-query -W -f='${Version}' perl-base)" \
    && dpkg --compare-versions "$perl_base_version" ge "5.36.0-7+deb12u4" \
    && rm -rf /var/lib/apt/lists/*

# Prevents Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY app ./app
COPY templates ./templates
COPY static ./static
COPY robots.txt ./robots.txt
COPY sitemap.xml ./sitemap.xml

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]
