ARG BUILD_FROM
FROM ${BUILD_FROM}

ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        cups \
        cups-daemon \
        cups-bsd \
        cups-client \
        cups-filters \
        printer-driver-escpr \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY rootfs/ /

RUN pip3 install --break-system-packages --no-cache-dir -r /app/requirements.txt \
    && chmod +x /etc/services.d/epson-maintenance-print/run
