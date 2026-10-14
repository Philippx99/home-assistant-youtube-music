# YouTube Music Browser für Home Assistant

Home Assistant App für YouTube Music mit Anmeldung über das normale Google-Anmeldefeld und Auswahl eines Home-Assistant-Media-Players.

## Installation

Füge dieses Repository in Home Assistant unter **Einstellungen → Apps → App-Store → ⋮ → Repositories** hinzu. Installiere anschließend **YouTube Music Browser**.

Beim ersten Start muss in den App-Optionen `stream_base_url` auf eine Adresse gesetzt werden, die dein Media-Player erreichen kann, z. B. `http://192.168.1.20:8099`. Danach öffnest du **YouTube Music** in der Home-Assistant-Seitenleiste, meldest dich an, wählst einen Player und verbindest ihn.

## Funktionsweise und Einschränkungen

Die App öffnet YouTube Music in Chromium. Der Browserton wird über einen virtuellen PulseAudio-Ausgang aufgenommen und als MP3-Livestream an den gewählten Media-Player weitergereicht. Der Player muss die konfigurierte Stream-Adresse erreichen und MP3-Livestreams unterstützen. Der Stream hat keine Such- oder Rücksprungfunktion.

## App-Quellcode

Der App-Ordner befindet sich unter [`youtube_music_browser`](youtube_music_browser/).
