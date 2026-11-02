# Источники для V3 и официальный набор Blender

## Официальный Human Base Meshes v1.4.1

- Архив уже присутствует в ветке `main` этого репозитория: [human-base-meshes-bundle-v1.4.1.zip](https://github.com/PandaGarry/family_studio/blob/main/human-base-meshes-bundle-v1.4.1.zip). Это тот самый файл, на который пользователь прислал ссылку.
- Git blob SHA-1: `2bf909f6af68b05ac394864f92a12a71630aaed1`; размер `50,643,039` байт.
- Полученная в рабочем окружении копия: SHA-256 `811f43accbb31a88266d932f8f5563b2d13586fca0ba2693aad1f5fe582b3515`; ожидаемая контрольная сумма совпала, `unzip -t` прошёл.
- Blender указывает лицензию CC0 для официального набора: <https://www.blender.org/download/demo-files/>.
- В Blender 5.2 WASM просмотрен `human_base_meshes_bundle.blend`. В официальной коллекции `Head - Stylized` есть `GEO-head_stylized` (4,118 вершин / 4,134 граней) и отдельные объекты глаз. Это нейтральная исходная голова, не Dad и не готовая likeness.
- Ветка не дублирует zip размером 50.6 MB: архив уже находится на `main` по ссылке выше.

## Временный источник V3 (не переносить дальше)

V3 был запущен на нейтральном файле Dan Ulrich из [`dan283/basemeshes`](https://github.com/dan283/basemeshes/blob/main/blender_neutral_head_midres_sculpt.blend), Git blob SHA-1 `b6cc3349b3610292ac55e4cf77a7321a7b8b647c`, локальный SHA-256 `a220f4aa77742fef9c93c231c686b02084a6ab4931f7159f3b41d0160218df30`. У upstream-репозитория нет отдельного файла лицензии, а байтовое совпадение с официальным v1.4.1 не подтверждалось. Поэтому этот временный файл не включён в ветку и не должен быть основой следующего прохода.
