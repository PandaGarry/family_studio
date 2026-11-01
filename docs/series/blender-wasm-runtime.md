# Браузерный Blender runtime: проверка среды

Статус: **технический browser smoke test пройден 2026-11-01; активный harness теперь намеренно остановлен.** Blender 5.2.0 LTS WebAssembly запускался в Chromium, Blender Python исполнил сцену, Cycles сохранил PNG, `.blend` был сохранён и переоткрыт. R3 blockout ранее получил 9/10 как proportion base, но пользователь позднее отверг его как неподходящий blockout/base; procedural R4 v1 получил 1/10. Оба mesh — только rejected archive, ни один не принят.

## Кандидат и локальная установка

Используется зафиксированный npm-пакет `@volter/blender-engine@0.1.148`: Blender 5.2.0 LTS, собранный в Emscripten WebAssembly. Это не нативный `blender` в shell и не официальный установщик Blender; это реальный Blender runtime в браузерном worker. Пакет выполняет Blender Python API и предоставляет `BlenderRuntime.nativePreview()`, запускающий Cycles.

Harness находится в [`tools/blender-wasm-runtime/`](../../tools/blender-wasm-runtime/):

```sh
cd tools/blender-wasm-runtime
npm install
npm run dev
```

Текущая стартовая страница — статусная заглушка: автоматически Blender не запускается и rejected blockout не пересобирается. Исторический runtime setup использовал `crossOriginIsolated === true`, `SharedArrayBuffer`, COOP `same-origin`, COEP `credentialless` и same-origin Brotli assets. Запуск Blender WASM технически возможен, но браузерный harness не предоставляет подтверждённый интерактивный sculpting workflow. Платный cloud/render service не используется.

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
3. Archived `src/dad_blockout_r3_rejected.py` исполнился через Blender Python API без traceback. Сцена сохранилась как один Blender mesh object из disconnected primitive shells, с viewport-only references, камерами front / three-quarter / profile и crewneck/no hood. Скрипт сохранён только как история и больше не подключён к active page.
4. `nativePreview()` подтвердил `renderer: CYCLES`, 360×640 и 32 samples; на тестовом Chromium один проход занял 9.65 s / 11.11 s / 6.41 s для трёх камер. Denoising upstream preview API отключает, так что это зернистые технические изображения.
5. Blender bridge сохранил сжатый `.blend` через chunk/hash round-trip. Следующий браузерный запуск Blender прочитал этот файл обратно; runtime затем пересохранил обновлённую сцену.

## Полученные файлы

- [`assets/models/dad/rejected/dad-blockout-r3-rejected.blend`](../../assets/models/dad/rejected/dad-blockout-r3-rejected.blend) — исторический Blender-файл, ранее загружавшийся повторным Blender 5.2 runtime.
- [`assets/renders/dad-blockout-r3-rejected/front.png`](../../assets/renders/dad-blockout-r3-rejected/front.png), [`three-quarter.png`](../../assets/renders/dad-blockout-r3-rejected/three-quarter.png), [`side.png`](../../assets/renders/dad-blockout-r3-rejected/side.png) — реальные native Cycles technical renders, не evidence качества модели.
- Скрипт перемещён в [`tools/blender-wasm-runtime/src/dad_blockout_r3_rejected.py`](../../tools/blender-wasm-runtime/src/dad_blockout_r3_rejected.py); active page переписана как статическая статусная страница, без импорта этого скрипта.

R3 раньше получил 9/10 как пропорциональная опора, но пользователь позднее отверг blockout как подходящую базу. Он состоит из primitive shells, без production topology/UV/rig/animation; теперь его статус — rejected archive, не hero model и не стартовая геометрия.

## R4 procedural study v1 — технически отрендерен, визуально отвергнут

Этот эксперимент сохранён отдельно от R3 для аудита процесса, но не считается рабочей hero-моделью:

- [`assets/models/dad/rejected/dad-procedural-v1.blend`](../../assets/models/dad/rejected/dad-procedural-v1.blend) — 2,443,966 bytes; SHA-256 `5e8d93c30b271b81fbd4cca6a7d8a945f4251fc03298576ec8299a9c2c1ec9e7`.
- Его five-view native Cycles renders перемещены в [`assets/renders/dad-procedural-v1-rejected/`](../../assets/renders/dad-procedural-v1-rejected/) (four full-body angles at 512×896/64 samples; face close-up at 512×512/80 samples).
- Сценарий сохранён как [`tools/blender-wasm-runtime/src/dad_procedural_v1_rejected.py`](../../tools/blender-wasm-runtime/src/dad_procedural_v1_rejected.py). Harness не направлен ни на R3, ни на R4: active page остановлена.

Runtime факт: Chromium isolation подтверждена; Blender 5.2 WASM прочитал `.blend`, исполнил Python, выполнил Cycles и сохранил файлы. Это говорит только о технической работоспособности. Пользователь оценил визуальный результат на **1/10** из-за колоссального расхождения с исходным образом. Причина — неправильный метод: простые параметрические shells/детали собраны напрямую по догадке, без точного side-by-side match и проверки головы до полной фигуры. Ни оболочки, ни script, ни renders не использовать как стартовую геометрию/визуальную цель.

Текущий процесс: не продолжать ни с R3, ни с R4 геометрии. Сначала reference audit и проверка реального интерактивного Blender sculpt/modeling path; затем custom model с точным side-by-side likeness/detail review. «Blender выполнил script» и «Cycles отрендерил PNG» — только техническая проверка, не доказательство качества персонажа.

## Лицензия

Пакет и собранный runtime предоставляются на условиях GPL-3.0-or-later; сведения о Blender и исходные notices сохранены в [`tools/blender-wasm-runtime/THIRD_PARTY_NOTICES.md`](../../tools/blender-wasm-runtime/THIRD_PARTY_NOTICES.md) и каталоге `THIRD_PARTY_LICENSES/`. Версия/источник зафиксированы в `package.json`, `package-lock.json` и upstream `BUNDLE.json` пакета. Не убирать эти файлы при распространении runtime.
