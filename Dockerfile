FROM ubuntu:22.04

# Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    inkscape \
    imagemagick \
    python3 \
    python3-pip \
    libmagickwand-dev \
    && rm -rf /var/lib/apt/lists/*

# Configure ImageMagick to allow PDF operations and large images
RUN sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' /etc/ImageMagick-6/policy.xml && \
    sed -i 's/<policy domain="resource" name="memory" value="[^"]*"/<policy domain="resource" name="memory" value="2GiB"/' /etc/ImageMagick-6/policy.xml && \
    sed -i 's/<policy domain="resource" name="disk" value="[^"]*"/<policy domain="resource" name="disk" value="4GiB"/' /etc/ImageMagick-6/policy.xml && \
    sed -i 's/<policy domain="resource" name="width" value="[^"]*"/<policy domain="resource" name="width" value="32KP"/' /etc/ImageMagick-6/policy.xml && \
    sed -i 's/<policy domain="resource" name="height" value="[^"]*"/<policy domain="resource" name="height" value="32KP"/' /etc/ImageMagick-6/policy.xml && \
    sed -i 's/<policy domain="resource" name="area" value="[^"]*"/<policy domain="resource" name="area" value="256MP"/' /etc/ImageMagick-6/policy.xml

# Install Python dependencies
RUN pip3 install Pillow Wand

# Set working directory
WORKDIR /app

# Copy conversion script
COPY convert.py /app/convert.py

# Make script executable
RUN chmod +x /app/convert.py

# Entry point
ENTRYPOINT ["python3", "/app/convert.py"]
