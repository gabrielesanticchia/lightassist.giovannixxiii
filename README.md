# LightAssist


Controlla strisce LED Bluetooth Low Energy di terze parti da Android, iOS e Web (PWA).
Open source, zero permessi internet, zero tracking.

## Protocolli supportati

| Protocollo | Dispositivi | Mic integrato |
|------------|-------------|:---:|
| ELK-BLEDOM | ELK-BLEDOM, ELK-BLEDOB, ELK-BLEDDM, ELK-BLE, ELK-BTC, ELK-BULB, ELK-BULB2, ELK-LAMPL, LEDBLE, LED-, JACKYLED, XROCKER, DMRRBA-007, Realky | ✅ |
| MELK | MELK, MELK-OA10, MELK-OC10, MELK-OF10, MELK-OG10, MELK-OA21 | ✅ (OA) |
| Triones | Triones-*, QHM-* | ❌ |
| SP | SP105E, SP110E, SP611E, SP621E | ❌ |
| LED-DMX | LED-DMX-00, LED-DMX-03 | ❌ |
| Colorful-Light | Colorful-Light | ❌ |
| LEDBlue | LEDBlue-* | ❌ |

## Funzionalità

- **Controllo completo**: RGB, brightness, speed, 22+ effetti, color temperature
- **Multi-device**: connetti e controlla più strisce contemporaneamente
- **Scenes**: preset istantanei (max 20), 1 tap per applicare
- **Macro**: sequenze temporizzate con step, loop, trigger (orari, connect/disconnect, boot)
- **Music Sync**: FFT → mappatura frequenza→colore (dispositivi con mic o mic telefono)
- **Riconnessione automatica** in background
- **Import/Export JSON** per scene e macro
- **Protocol Test**: invio frame hex arbitrario (debug)

## Piattaforme

| Piattaforma | Build | Note |
|-------------|-------|------|
| Android | `flutter build appbundle` | Min API 26 |
| iOS | `flutter build ipa` | Min iOS 14, serve account Apple Developer |
| Web (PWA) | `vite build` | Solo Chrome/Edge, richiede HTTPS o localhost |

## Requisiti

### Flutter
- Dart 3+, Flutter   
