# Ревизия и перенос из `PandaGarry/docuflow`

Дата проверки: 2026-11-01. Исходник: публичный репозиторий пользователя `PandaGarry/docuflow`, `main` на коммите `6c8023123ab8130b7a3b61b0c2b836b5b06a1de9`. Пользователь явно разрешил использовать материалы оттуда в Family Studio.

## Что уже перенесено

В `assets/references/docuflow/characters/{dad,mom,son}/` скопированы исходные master-turnaround, master-face, вырезанные виды front/3/4/profile и `character.json` всех трёх героев (15 PNG + 3 JSON, около 10.9 MB). Файлы не перерисовывались и не очищались; зелёный фон на turnaround оставлен частью **референс-листа**, а не персонажа. Источник, commit и правила использования описаны в [`assets/references/docuflow/README.md`](../../assets/references/docuflow/README.md).

Эти мастера дают более чистые и пригодные для моделирования виды, чем прежние скриншоты с UI. Старые файлы в `assets/references/raw/` сохранены; новые не заменяют оригиналы и становятся основными modeling references после подтверждения автором.

## Документы и API, проверенные в источнике

- [3D-renderer и причины отказа от Blender в старом sandbox](https://github.com/PandaGarry/docuflow/blob/6c8023123ab8130b7a3b61b0c2b836b5b06a1de9/docs/19-3D.md)
- [Анатомия и известные ограничения модели папы](https://github.com/PandaGarry/docuflow/blob/6c8023123ab8130b7a3b61b0c2b836b5b06a1de9/docs/20-P1-ANATOMY.md)
- [21-костный риг, IK и заявленные тесты](https://github.com/PandaGarry/docuflow/blob/6c8023123ab8130b7a3b61b0c2b836b5b06a1de9/docs/21-RIG.md)
- [Журнал решений и статус 3D-ветки](https://github.com/PandaGarry/docuflow/blob/6c8023123ab8130b7a3b61b0c2b836b5b06a1de9/docs/26-LOG.md)
- [Канон образов и известные расхождения](https://github.com/PandaGarry/docuflow/blob/6c8023123ab8130b7a3b61b0c2b836b5b06a1de9/docs/29-CANON.md)
- Код: [`body3d.py`](https://github.com/PandaGarry/docuflow/blob/6c8023123ab8130b7a3b61b0c2b836b5b06a1de9/studio/engine/body3d.py), [`rig3d.py`](https://github.com/PandaGarry/docuflow/blob/6c8023123ab8130b7a3b61b0c2b836b5b06a1de9/studio/engine/rig3d.py), [`character.py`](https://github.com/PandaGarry/docuflow/blob/6c8023123ab8130b7a3b61b0c2b836b5b06a1de9/studio/engine/character.py), [`animation.py`](https://github.com/PandaGarry/docuflow/blob/6c8023123ab8130b7a3b61b0c2b836b5b06a1de9/studio/engine/animation.py), [`render3d.py`](https://github.com/PandaGarry/docuflow/blob/6c8023123ab8130b7a3b61b0c2b836b5b06a1de9/studio/engine/render3d.py).

## Что обнаружено в источнике

| Слой | Где в `docuflow` | Решение для Family Studio |
|---|---|---|
| Канонические изображения и карточки героев | `studio/characters/{dad,mom,son}/` | Уже перенесены как неизменённые modeling references. Мама и сын пока остаются резервом; первым собираем папу. |
| Дополнительные отцовские мастера, позы, эмоции, visemes и циклы | `studio/2p5d/dad/`, `studio/out/` | Не копировать библиотеку целиком. Использовать выборочно как справочник ракурсов, acting и тайминга после визуальной проверки каждого файла. |
| Процедурная геометрия | `studio/engine/body3d.py`, `render3d.py`, `sculpt.py`, `sdf.py` | Изучено как источник параметров и идей. Код пока не перенесён в проект и не считается Blender-геометрией. |
| Скелет/позирование/анимация | `studio/engine/rig3d.py`, `character.py`, `animation.py`; `docs/21-RIG.md` | Сохранить как справочник по FK/IK, foot lock и тестам движения. Не объявлять его Blender-ригом и не переносить без проверки интерфейсов/зависимостей. |
| Отцовские motion references | `studio/out/dad-walk-rig-sheet.png`, `dad-run-rig-sheet.png`, `dad-walk-poses.png`, `dad-run-rig.mp4` | Выборочно перенесены в `assets/references/docuflow/motion/`. Статичные листы просмотрены: заметны обрезания головы/тела и разрывы/артефакты конечностей. Допустимы только как подсказка тайминга/направления поз; не использовать как визуальный baseline, не выдавать за Blender-анимацию. Сам MP4 не просматривался и не считается проверенным. |
| Остальные выходные ролики | `studio/out/dad-walk.mp4`, `dad-face*.mp4`, `dad-motion-test.mp4` и другие | Не перенесены и визуально не проверены; ссылки на них не служат доказательством качества текущего проекта. |

## Существенное различие: 3D-прототип — не Blender

Проверка дерева обеих веток `docuflow` не нашла `.blend`, `.blend1`, `project.godot` или сцен Godot. Ветка, названная 3D, — собственная программная mesh/SDF-система на Python/NumPy с растеризатором из `studio/engine/render3d.py`, а не проект Blender или Godot.

В документации `docuflow` заявлены процедурная блокировка папы, 21-костный скелет, IK, walk/idle и тесты рига. Технический API — `body3d.Proportions` / `build_body`, `character.Character.build(pose) -> list[Mesh]`, `rig3d.Skeleton.from_proportions`, `animation.Walk.pose_at(t)`. `Mesh` хранит NumPy-массивы `verts (N,3)`, `tris (M,3)`, normals, vertex color, AO и roughness; используется собственная Y-up-система координат. При переносе потребовались бы адаптация осей, материалов и пересборки поз, а не простой импорт готового armature. `Character.build` пересобирает конечности и применяет собственную skinning-функцию к торсу; Blender-экспортера или `bpy`-риг-контракта в исходнике нет. Ядро зависит от NumPy, PNG-рендер использует Pillow.

Для оценки был отдельно запущен код `main` из временной папки с NumPy/Pillow: `Proportions(height_heads=5.9, belly=1.06)`, `turnaround(size=(420,700), ss=1)` и `face_closeup`; использовалась стандартная палитра движка, не identity/color match. Пробные front/3⁄4/profile/face кадры не сохранены как assets проекта. Это подтвердило работу только **кастомного software renderer**, не Blender. Визуально P1 всё ещё заметно расходится с canonical master: лицо читается как упрощённая геометрическая маска, тело стройнее/обобщённее мастера, волосы/борода и одежда упрощены, а в модели уже зашит капюшон. Это согласуется с `docs/20-P1-ANATOMY.md`, где прямо перечислены незакрытые пробелы, и с `docs/26-LOG.md`, который отмечает отказ от этой ветки по качеству. Поэтому это полезный технический прототип и справочник, но **не утверждённый герой, не финальный рендер и не proof-of-style**.

В `docs/21-RIG.md` указано «57/57» проверок; это число взято из документа источника и здесь не воспроизводилось. Тесты рига и MP4 в Family Studio не запускались/не просматривались; обзорные PNG-листы показали заметные обрезания и стыковые артефакты. Blender/Godot runtime в текущем sandbox ранее не был доступен. Не переносить заявления источника в статус проверенных результатов Family Studio.

## Канонический приоритет и обнаруженные противоречия

1. **Первый герой — папа.** Его clean turnaround и face-master перенесены и должны стать основой одного Blender-меша; предварительный brief — [`dad-3d-model-brief.md`](dad-3d-model-brief.md).
2. Для формы головы и тела использовать front, 3/4 и side как одновременные референсы; не проецировать зелёный фон и не подменять поворот сменой картинок.
3. Визуальный turnaround папы показывает светлый серый crewneck без видимого капюшона, а `character.json` называет домашний верх `hoodie_gray`. До утверждения одежды не дорисовывать капюшон и не выдавать JSON-ярлык за точное описание видимого мастера.
4. Документированный параметр `height_heads: 5.9` — полезная стартовая оценка, не точный размер. Рост и ширину нужно проверить по чистым views и семейному lineup.
5. Старые циклы папы могут быть полезны для поз и ритма, но это не автоматически пригодные 3D motion curves: контакт, пропорции и выступающие детали нужно сопоставлять с новым ригом.

## План миграции

- **Сейчас:** закрепить перенесённые masters, обновить reference brief и сделать согласуемый серый blockout папы в Blender.
- **После утверждения blockout:** собрать лицо/волосы/бороду и одежду отдельными управляемыми формами, затем armature и facial controls.
- **Движение:** использовать записанные в `docs/21-RIG.md` решения (IK-контакт стоп, противофаза рук, дыхание и weight shift) как checklist, а не копировать непроверенную реализацию вслепую. Первый тест — idle/blink/взгляд/поворот/жест и несколько шагов.
- **Порт кода:** если интерфейсы и качество геометрии окажутся полезны, сделать отдельный проверяемый адаптер из структур меша/поз в Blender. Не встраивать software rasterizer в финальный render pipeline.
- **Approval gate:** один и тот же Blender mesh должен пройти front/3/4/profile, close-up и короткое движение; только тогда артефакт можно назвать 3D proof-of-style.

## Что намеренно не сделано

Не копировался весь `docuflow`, не переносились тысячи производных изображений/видео и не копировался Python-рендерер в production-код. Причины: объём и неодинаковое QA ассетов, отдельная лицензия на код в источнике не обнаружена, а старая 3D-ветка сама помечена как недостаточно качественная. Визуальные мастера пользователя сохранены выборочно с provenance; код можно портировать отдельно после целевого теста.