# Blender models — Dad

## Статус: сейчас нет одобренной 3D-модели

Пользователь ранее оценил R3 gray blockout на 9/10 как пропорциональную основу, но затем отдельно уточнил, что **blockout тоже не подходит** и не должен служить базой. Поэтому историческую оценку сохраняем в журнале, но текущая граница решения — R3 не принят как подходящая модель/основа. Его `.blend`, renders и script перемещены в rejected archive; не продолжать от этой геометрии и не выдавать её в активном harness.

- [`rejected/dad-blockout-r3-rejected.blend`](rejected/dad-blockout-r3-rejected.blend) — прежний серый примитивный blockout, архив только для истории.
- [`../../renders/dad-blockout-r3-rejected/`](../../renders/dad-blockout-r3-rejected/) — соответствующие технические Cycles previews, не quality evidence.
- [`../../../tools/blender-wasm-runtime/src/dad_blockout_r3_rejected.py`](../../../tools/blender-wasm-runtime/src/dad_blockout_r3_rejected.py) — архивный генератор, не активный modeling workflow.

## Отклонённая процедурная R4 v1 — архив

Следующая полнофигурная процедурная study получила от пользователя **1/10** и однозначно отвергнута. Она хранится отдельно в [`rejected/dad-procedural-v1.blend`](rejected/dad-procedural-v1.blend); исходник и рендеры перечислены в предыдущей истории/серийных документах. Её геометрию, как и R3 blockout, не использовать как modeling base.

Оба набора файлов фиксируют ошибки подхода. Факт технического создания `.blend` и Cycles renders не означает художественную приёмку.

## Следующий этап

Сейчас **нет принятой 3D-базы**. Перед новой геометрией выполнить reference audit: выровнять утверждённые masters, разобрать видимые landmarks/силуэты/мелкие детали и проверить согласованность видов. Затем использовать реальное ручное моделирование/скульптинг в полноценном Blender workflow, а не procedural primitives. Новый пользовательский результат должен быть детализированным и проверенным side-by-side с референсом; rough blockout не выдавать как hero model или как принятую основу. Критерии и ограничения среды записаны в [`docs/series/roadmap.md`](../../../docs/series/roadmap.md) и [`docs/series/dad-3d-model-brief.md`](../../../docs/series/dad-3d-model-brief.md).
