# Blender models — Dad

## Статус: сейчас нет одобренной 3D-модели

Пользователь ранее оценил R3 gray blockout на 9/10 как пропорциональную основу, но затем отдельно уточнил, что **blockout тоже не подходит** и не должен служить базой. Поэтому историческую оценку сохраняем в журнале, но текущая граница решения — R3 не принят как подходящая модель/основа. Его `.blend`, renders и script перемещены в rejected archive; не продолжать от этой геометрии и не выдавать её в активном harness.

- [`rejected/dad-blockout-r3-rejected.blend`](rejected/dad-blockout-r3-rejected.blend) — прежний серый примитивный blockout, архив только для истории.
- [`../../renders/dad-blockout-r3-rejected/`](../../renders/dad-blockout-r3-rejected/) — соответствующие технические Cycles previews, не quality evidence.
- [`../../../tools/blender-wasm-runtime/src/dad_blockout_r3_rejected.py`](../../../tools/blender-wasm-runtime/src/dad_blockout_r3_rejected.py) — архивный генератор, не активный modeling workflow.

## Отклонённая процедурная R4 v1 — архив

Следующая полнофигурная процедурная study получила от пользователя **1/10** и однозначно отвергнута. Она хранится отдельно в [`rejected/dad-procedural-v1.blend`](rejected/dad-procedural-v1.blend); исходник и рендеры перечислены в предыдущей истории/серийных документах. Её геометрию, как и R3 blockout, не использовать как modeling base.

Оба набора файлов фиксируют ошибки подхода. Факт технического создания `.blend` и Cycles renders не означает художественную приёмку.

## Официальная база Blender Human Base Meshes v1.4.1 — скачана и проверена

- Архив находится в [`main` этого репозитория](https://github.com/PandaGarry/family_studio/blob/main/human-base-meshes-bundle-v1.4.1.zip). Он скачан и проверен: размер `50,643,039` байт, SHA-256 `811f43accbb31a88266d932f8f5563b2d13586fca0ba2693aad1f5fe582b3515`, ZIP integrity test прошёл. Повторно добавлять 50.6 MB архив в эту ветку не нужно. Официальный Blender Demo Files указывает для набора лицензию CC0.
- В Blender 5.2 WASM просмотрено содержимое архива. `GEO-head_stylized` (4,118 вершин / 4,134 граней) и отдельные стилизованные глаза выглядят более уместной официальной базой для следующего head/bust study. Это пока нейтральная база, не Dad и не одобренная likeness.
- Технические сведения и контрольные суммы записаны в [`sources/SOURCE.md`](sources/SOURCE.md).

## Ранее использованный запасной кандидат

V3 начинался с временного нейтрального sculpting-варианта Dan Ulrich. Его происхождение и отсутствие отдельной лицензии отмечены в [`sources/SOURCE.md`](sources/SOURCE.md); сам файл не включён в ветку. Он не является архивом v1.4.1 и не должен подменять официальную базу в следующем проходе.

## V4 — отдельный диагностический study от официальной базы (не утверждён)

- V4 собран отдельной копией официального `GEO-head_stylized` из Blender Human Base Meshes v1.4.1; исходный архив и исходный `.blend` не изменялись. Основа CC0, исходная сетка содержит 4,118 вершин / 4,134 грани.
- Генератор [`dad_head_study_v4.py`](../../../tools/blender-wasm-runtime/src/dad_head_study_v4.py) делает программные правки геометрии: трансформы запекаются, челюсть и шея слегка расширяются, затылок сохраняет выпуклый профиль; волосы/борода остаются интегрированными с головой без отдельной сферической шапки и shell-артефактов. Это скриптовая геометрия, не ручная скульптура.
- Cycles PNG: [`front.png`](../../renders/dad-head-study-v4/front.png), [`three-quarter.png`](../../renders/dad-head-study-v4/three-quarter.png), [`profile.png`](../../renders/dad-head-study-v4/profile.png), [`face-closeup.png`](../../renders/dad-head-study-v4/face-closeup.png). Сравнительная доска [`reference-comparison-review.png`](../../renders/dad-head-study-v4/reference-comparison-review.png).
- **V4 не принят:** сходство остаётся низким; причёска не повторяет эталонный объём/укладку, борода не имеет требуемой выразительной формы, а посадка глаз и веки всё ещё требуют художественной доработки. Рендеры — диагностические и не являются доказательством готовности.
- Полученный Blender study находится только в игнорируемой runtime-папке; в `assets/models/dad/studies/` он не включается как готовая модель.

V3 остаётся отдельным диагностическим материалом от неподходящего временного кандидата: [`reference-comparison-review.png`](../../renders/dad-head-study-v3/reference-comparison-review.png). Одобренной 3D-модели по-прежнему нет. Следующие изменения не должны начинаться с V1/V2/R3/R4, V3 или запасного Dan2-файла; V4 допускается лишь как техническая отправная точка, но его likeness также не утверждён.
