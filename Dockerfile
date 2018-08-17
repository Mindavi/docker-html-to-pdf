FROM debian:stretch-slim

#### WKHTMLTOPDF ####
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    curl \
    fontconfig \
    libjpeg62-turbo \
    libx11-6 \
    libxcb1 \
    libxext6 \
    libxrender1 \
    xfonts-75dpi \
    xfonts-base
RUN curl --silent https://downloads.wkhtmltopdf.org/0.12/0.12.5/wkhtmltox_0.12.5-1.stretch_amd64.deb --output wkhtmltopdf.deb --location
RUN dpkg -i wkhtmltopdf.deb
# fix kerning issues https://github.com/wkhtmltopdf/wkhtmltopdf/issues/45#issuecomment-108649125
COPY font-fix.conf /etc/fonts/conf.d/100-wkhtmltoimage-special.conf
#### END WKHTMLTOPDF ####

#### WEBSERVER ####
# Install dependencies for running web service
RUN apt-get update && apt-get upgrade -y && apt-get install -y python3 python3-pip
RUN pip3 install werkzeug executor gunicorn

RUN mkdir ./src

EXPOSE 80
ENTRYPOINT ["usr/local/bin/gunicorn"]
CMD ["--chdir", "src", "-b", "0.0.0.0:80", "--log-file", "-", "app:application"]

#### END WEBSERVER ####