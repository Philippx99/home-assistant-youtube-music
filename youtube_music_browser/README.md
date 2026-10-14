# YouTube Music Browser für Home Assistant

Das Add-on zeigt YouTube Music in einer Browser-App im Home-Assistant-Seitenmenü. Du meldest dich dort mit dem normalen Google-Anmeldefeld an. Chromium gibt seinen Ton auf einen virtuellen PulseAudio-Ausgang aus; das Add-on erfasst diesen Ton und stellt ihn als MP3-Livestream bereit. Über **Player verbinden** weist du einen Home-Assistant-Media-Player an, diesen Audiostream abzuspielen.

## Installation

1. Kopiere den gesamten Projektordner in den Samba-Share `local_apps` nach `youtube_music_browser/`, sodass `/local_apps/youtube_music_browser/config.yaml` existiert. Alternativ kannst du ihn als Git-Repository bereitstellen und unter **Einstellungen → Apps → App-Store → ⋮ → Repositories** hinzufügen.
2. Installiere **YouTube Music Browser** und starte das Add-on.
3. Öffne die Add-on-Optionen und setze `stream_base_url` auf die IP-Adresse und den Port, die dein Media-Player erreichen kann, z. B. `http://192.168.1.20:8099`. Port 8099 ist für den Livestream freigegeben.
4. Öffne **YouTube Music** im Home-Assistant-Seitenmenü. Melde dich an, wähle einen Player und drücke **Player verbinden**. Starte anschließend die Musikwiedergabe im Browser.

## Grenzen

- Der Player muss den Livestream unter `stream_base_url` erreichen und MP3-Livestreams wiedergeben können. Das hängt von der jeweiligen Player-Integration ab.
- Setze `stream_base_url` passend zum Netzwerk des Players. Eine interne Host-Adresse funktioniert nicht, wenn der Player sie nicht erreichen kann.
- Das Add-on streamt den Browser-Ton live. Verbinde den Player zuerst und starte danach den Titel; der Stream hat keine Suchleiste oder Rücksprungfunktion.
- Der Browser spielt den Ton über den virtuellen Audioausgang des Add-ons. Die lokale Browser-App gibt den Ton daher nicht zusätzlich über den Computerlautsprecher aus.
- Der Image-Build benötigt Internetzugriff.

## Version 1.0.9

Enthält zusätzliche Startmeldungen für PulseAudio, Xvfb, x11vnc und websockify. Sie zeigen im Add-on-Protokoll, an welcher Stelle der Browser- oder VNC-Start hängen bleibt.

## Version 1.0.10

PulseAudio wird jetzt direkt von s6 überwacht. Das Socket-Verzeichnis ist für den PulseAudio-Systemdienst beschreibbar; Startfehler erscheinen im Add-on-Protokoll.

## Version 1.0.11

Behebt eine Zurückweisung der PulseAudio-Clientverbindung durch die zusätzliche Cookie-Authentifizierung am lokalen Unix-Socket.

## Version 1.0.12

Verhindert, dass die PulseAudio-Standardkonfiguration denselben Unix-Socket belegt wie die Add-on-Konfiguration.

## Version 1.0.13

Reduziert die Pufferung beim PulseAudio-Eingang, beim MP3-Ausgang und beim HTTP-Stream.
