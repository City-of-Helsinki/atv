# ==============================
FROM registry.access.redhat.com/ubi9/python-312 AS appbase
# ==============================

EXPOSE 8000/tcp

USER root

RUN yum --disableplugin subscription-manager -y --allowerasing update \
    && yum --disableplugin subscription-manager -y install pcre-devel nmap-ncat \
    && yum --disableplugin subscription-manager -y clean all

COPY scripts /scripts
ENV PATH="/scripts:${PATH}"

RUN setup_user.sh
RUN mkdir /app && chown -R 1000:0 /app

## Need to set the permissions beforehand for the Attachment directory
## https://github.com/docker/compose/issues/3270#issuecomment-363478501
RUN mkdir -p /var/media && chown -R 1000:0 /var/media && chmod g=u -R /var/media
RUN mkdir -p /var/static && chown -R 1000:0 /var/static && chmod g=u -R /var/static

WORKDIR /app

COPY --chown=1000:0 requirements.txt /app/requirements.txt
COPY --chown=1000:0 requirements-prod.txt /app/requirements-prod.txt
COPY --chown=1000:0 .prod/escape_json.c /app/.prod/escape_json.c
USER 1000

RUN pip install -U pip setuptools wheel \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && pip install --no-cache-dir -r /app/requirements-prod.txt \
    && uwsgi --build-plugin /app/.prod/escape_json.c \
    && mv /app/escape_json_plugin.so /app/.prod/escape_json_plugin.so

COPY --chown=1000:0 docker-entrypoint.sh /entrypoint/docker-entrypoint.sh
ENTRYPOINT ["/entrypoint/docker-entrypoint.sh"]

# ==============================
FROM appbase AS development
# ==============================

COPY --chown=1000:0 requirements-dev.txt ./requirements-dev.txt
RUN pip install --no-cache-dir -r ./requirements-dev.txt

ENV DEV_SERVER=1

COPY --chown=1000:0 . /app/

# ==============================
FROM appbase AS staticbuilder
# ==============================

ENV STATIC_ROOT /var/static
COPY --chown=1000:0 . /app/
RUN SECRET_KEY="only-used-for-collectstatic" python manage.py collectstatic --noinput

# ==============================
FROM appbase AS production
# ==============================

# fatal: detected dubious ownership in repository at '/app'
RUN git config --global --add safe.directory /app

COPY --from=staticbuilder --chown=1000:0 /var/static /var/static
COPY --chown=1000:0 . /app/
