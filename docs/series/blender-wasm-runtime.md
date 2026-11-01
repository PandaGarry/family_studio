# Браузерный Blender runtime: проверка среды

Статус: **browser smoke test пройден 2026-11-01.** Blender 5.2.0 LTS WebAssembly реально запущен в Chromium; Blender Python исполнил сцену, native Cycles сохранил три PNG, `.blend` сохранён и затем снова открыт Blender. Пользователь оценил blockout на 9/10 и одобрил его как базу для следующей фазы, но это не approval полноценной hero model.

## Кандидат и локальная установка

Используется зафиксированный npm-пакет `@volter/blender-engine@0.1.148`: Blender 5.2.0 LTS, собранный в Emscripten WebAssembly. Это не нативный `blender` в shell и не официальный установщик Blender; это реальный Blender runtime в браузерном worker. Пакет выполняет Blender Python API и предоставляет `BlenderRuntime.nativePreview()`, запускающий Cycles.

Harness находится в [`tools/blender-wasm-runtime/`](../../tools/blender-wasm-runtime/):

```sh
cd tools/blender-wasm-runtime
npm install
npm run dev
```

Страница автоматически начинает тест только если браузер сообщает `crossOriginIsolated === true` и поддерживает `SharedArrayBuffer`. Dev server отправляет COOP `same-origin` и COEP `credentialless`, обслуживает runtime-файлы по same-origin endpoints и Brotli-артефакты с `Content-Encoding: br`. Платный cloud/render service не используется. Для этой Emscripten-сборки обязательны cross-origin isolation и рабочий браузерный WebAssembly worker.

## Что уже проверено в этой среде

- Node.js 22.22.3, npm 10.9.8; Vite 8.3.5 и `@volter/blender-engine@0.1.148` установлены по точным версиям; `npm install` сообщил 0 vulnerabilities.
- `npm run build` успешно собирает страницу и worker bundle.
- Vite API отвечает `available: true`, `skew: emscripten`, перечисляет ожидаемые размеры и Brotli encoding.
- Brotli-ответы WASM, `.data` и Essentials распакованы и сопоставлены с SHA-256 из upstream manifests; все три совпали.
- Сервер корректно отдаёт абсолютный проектный root и четыре исходных Dad references для чтения Blender-сессией.
- Нативных Chromium/Firefox заранее в shell не было; для smoke test во временную папку `/tmp` установлены `@sparticuz/chromium@153.0.0` и `playwright-core@1.64.1` (не добавлены в Family Studio dependencies). Chromium сообщил `crossOriginIsolated: true`, `SharedArrayBuffer` доступен.
- `BlenderRuntime.start()` запустил Blender 5.2.0 LTS; runtime сообщил движки `CYCLES`, `BLENDER_EEVEE`, `BLENDER_WORKBENCH`, `VOLTER_THREE`. Python blockout исполнился без traceback; три Cycles preview PNG получены, document bridge сохранил `.blend`. Следующий запуск успешно открыл сохранённый файл по тому же пути.
- Upstream runtime печатает предупреждение `Unable to find the Python binary, the multiprocessing module may not be functional!`; harness и эти рендеры обходятся без Python multiprocessing. `nativePreview` upstream отключает denoising, поэтому Cycles images остаются зернистыми техническими blockout-превью.
- Проверка охватывает именно браузерный Blender WASM этой сборки, а не нативный shell executable или официальную дистрибуцию Blender.

## Фактически подтверждённый browser smoke test

1. Chromium 153 сообщил `crossOriginIsolated: true`; `SharedArrayBuffer` доступен, Vite COOP/COEP headers сохраняются и на маршрутах WASM-worker.
2. `BlenderRuntime.start()` запустил Blender 5.2.0 LTS; startup banner перечислил нативные `CYCLES`, `BLENDER_EEVEE` и `BLENDER_WORKBENCH`.
3. `src/dad_blockout.py` исполнился через Blender Python API без traceback. Сцена сохранилась как один Blender mesh object из disconnected primitive shells, с viewport-only references, камерами front / three-quarter / profile и crewneck/no hood.
4. `nativePreview()` подтвердил `renderer: CYCLES`, 360×640 и 32 samples; на тестовом Chromium один проход занял 9.65 s / 11.11 s / 6.41 s для трёх камер. Denoising upstream preview API отключает, так что это зернистые технические изображения.
5. Blender bridge сохранил сжатый `.blend` через chunk/hash round-trip. Следующий браузерный запуск Blender прочитал этот файл обратно; runtime затем пересохранил обновлённую сцену.

## Полученные файлы

- [`assets/models/dad/dad-blockout.blend`](../../assets/models/dad/dad-blockout.blend) — реальный Blender-файл, около 2.56 MB; загружался повторным Blender 5.2 runtime.
- [`assets/renders/dad-blockout/front.png`](../../assets/renders/dad-blockout/front.png), [`three-quarter.png`](../../assets/renders/dad-blockout/three-quarter.png), [`side.png`](../../assets/renders/dad-blockout/side.png) — реальные native Cycles PNG, по 360×640.
- Точная генерация описана в [`tools/blender-wasm-runtime/src/dad_blockout.py`](../../tools/blender-wasm-runtime/src/dad_blockout.py), запуск/сохранение — в [`src/main.js`](../../tools/blender-wasm-runtime/src/main.js).

Эти файлы фиксируют R3 blockout, который пользователь оценил на 9/10 и принял как рабочую основу. Но геометрия всё ещё состоит из primitive shells внутри одного mesh object: нет clean production topology, UV, weights, body/facial rig или анимации. Этот артефакт не является hero model.

## R4: Dad hero model v1 — фактический Blender-run

Отдельно сохранены новые артефакты; исходный R3 blockout не затирался:

- [`assets/models/dad/dad-hero-v1.blend`](../../assets/models/dad/dad-hero-v1.blend) — 2,443,966 bytes; SHA-256 `5e8d93c30b271b81fbd4cca6a7d8a945f4251fc03298576ec8299a9c2c1ec9e7`; отдельная сцена Blender 5.2.0 с полнофигурным цветным статическим персонажем, компонентами головы/лица/волос/бороды/одежды/обуви и review cameras.
- [`assets/renders/dad-hero-v1/front.png`](../../assets/renders/dad-hero-v1/front.png), [`three-quarter.png`](../../assets/renders/dad-hero-v1/three-quarter.png), [`side.png`](../../assets/renders/dad-hero-v1/side.png), [`back.png`](../../assets/renders/dad-hero-v1/back.png) — native Cycles, 512×896, 64 samples.
- [`assets/renders/dad-hero-v1/face-closeup.png`](../../assets/renders/dad-hero-v1/face-closeup.png) — native Cycles, 512×512, 80 samples.
- Сцену строит [`tools/blender-wasm-runtime/src/dad_hero_v1.py`](../../tools/blender-wasm-runtime/src/dad_hero_v1.py); странице harness добавлены пять review views и отдельный artifact allowlist.

Chromium cross-origin isolation и `SharedArrayBuffer` были проверены; Blender 5.2 WASM прочитал предыдущий v1 `.blend`, исполнил Python-сцену и сохранил обновлённый файл. В runtime-логе подтверждены Cycles и разрешения/число samples; полные ракурсы занимали примерно 44–84 секунды, close-up лица — около 75 секунд. Это настоящие Cycles render frames, не скриншоты Blender UI.

**Честный статус R4:** v1 — первый полный статический 3D-образ, не профессиональная финальная модель и не sign-off likeness. Силуэт/лицо/волосы/борода требуют дальнейшего сравнения с references; некоторые поверхности пока процедурные и упрощённые. Нет утверждённой production retopology, UV, armature, weights, facial controls или движения. Следующая итерация — улучшить likeness и органичность геометрии, после чего отдельно пройти topology, rig и motion gates из [`roadmap.md`](roadmap.md). Никакой Cycles beauty render не заменяет эти проверки.

## Лицензия

Пакет и собранный runtime предоставляются на условиях GPL-3.0-or-later; сведения о Blender и исходные notices сохранены в [`tools/blender-wasm-runtime/THIRD_PARTY_NOTICES.md`](../../tools/blender-wasm-runtime/THIRD_PARTY_NOTICES.md) и каталоге `THIRD_PARTY_LICENSES/`. Версия/источник зафиксированы в `package.json`, `package-lock.json` и upstream `BUNDLE.json` пакета. Не убирать эти файлы при распространении runtime.
