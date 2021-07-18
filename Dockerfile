FROM python:3.8-slim

# cloud-governance latest version
ARG VERSION

# install gitleaks
ARG gitleaks_version=7.0.2
RUN apt-get update \
     && apt-get install -y wget \
     && export VER=${gitleaks_version}  \
     && wget https://github.com/zricethezav/gitleaks/releases/download/v$VER/gitleaks-linux-amd64 \
     && mv gitleaks-linux-amd64 gitleaks \
     && chmod +x gitleaks \
     && mv gitleaks /usr/local/bin/ \
     && gitleaks --version

# install & run cloud-governance
RUN python -m pip install --upgrade pip && pip install cloud-governance==$VERSION
RUN pip3 --no-cache-dir install --upgrade awscli
ADD cloud_governance/policy /usr/local/cloud_governance/policy/
COPY cloud_governance/main/main.py /usr/local/cloud_governance/main.py

CMD [ "python", "/usr/local/cloud_governance/main.py"]
