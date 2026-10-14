FROM ghcr.io/home-assistant/base:latest
RUN apk add --no-cache bash chromium xvfb x11vnc fluxbox nginx python3 pulseaudio pulseaudio-utils ffmpeg websockify
COPY rootfs /
RUN chmod a+x /etc/services.d/youtube/run /etc/services.d/api/run /etc/services.d/vnc/run /etc/services.d/nginx/run /etc/services.d/audio/run
EXPOSE 8099
