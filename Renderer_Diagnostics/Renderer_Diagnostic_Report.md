# Renderer: диагностический отчёт

## Итог и разделение задач

- PPTX создан: Digital_Analyst_1C_v1.pptx, 15 слайдов.
- Markdown создан: Digital_Analyst_1C_v1.md.
- Структура презентации проверена: 5 тестов прошли.
- PDF не экспортирован. Независимый PDF по тексту не создавался.
- Визуальный рендер не проверен.
- Renderer не восстановлен: последний контрольный запуск завершился с кодом 139.
- После указания не менять инфраструктуру выполнялись только диагностика и формирование отчёта. Новые пакеты и сервисы не добавлялись.

## а) Среда исполнения renderer

Проверена непосредственно SSH-среда, запускающая бинарный файл, не компьютер Андрея и не предположительная среда Telegram-шлюза.

```json
{
  "os": {
    "NAME": "Debian GNU/Linux",
    "ID": "debian",
    "PRETTY_NAME": "Debian GNU/Linux 12 (bookworm)",
    "VERSION_ID": "12",
    "VERSION": "12 (bookworm)",
    "VERSION_CODENAME": "bookworm",
    "HOME_URL": "https://www.debian.org/",
    "SUPPORT_URL": "https://www.debian.org/support",
    "BUG_REPORT_URL": "https://bugs.debian.org/"
  },
  "architecture": "x86_64",
  "uid": 10000,
  "gid": 10000,
  "user": "athena",
  "collector_python": "/var/lib/hermes/workspace/tools/presentations/venv/bin/python",
  "collector_cwd": "/var/lib/hermes/workspace",
  "dockerenv_marker": true,
  "container_note": "Container marker is an observation; host Docker image ID and gateway runtime are not inferred from the SSH executor."
}
```

Наличие /.dockerenv — признак контейнера. Точный Docker image ID и параметры хостового контейнера из этой среды не установлены.

## б) Hermes, skill и Python

Версия работающего Hermes **не установлена из отдельного SSH executor**. CLI Hermes в нём не найден. Это не означает отсутствия Hermes в Telegram-шлюзе. Для подтверждения версии работающего шлюза нужен его собственный /version или метаданные установленного кода; подставлять версию навыка вместо версии Hermes нельзя.

```json
{
  "loaded_skill_api_path": "/var/lib/hermes/skills/productivity/powerpoint/SKILL.md",
  "loaded_skill_version": "1.1.0",
  "skill_helpers_api_directory": "/var/lib/hermes/skills/productivity/powerpoint/scripts",
  "executor_skill_copy": "/home/athena/.hermes/skills/productivity/powerpoint/SKILL.md",
  "builder_actually_used": "/var/lib/hermes/workspace/projects/1c-digital-analyst-presentation/build_deck.py",
  "actual_builder_interpreter": "/var/lib/hermes/workspace/tools/presentations/venv/bin/python",
  "note": "The task used custom build_deck.py with python-pptx, not the bundled pptx_create.py.",
  "python-pptx": "1.0.2",
  "pypdfium2": "5.14.0"
}
```

Загруженный навык содержит helpers: pptx_create.py, pptx_read.py, pptx_edit.py, pptx_from_template.py, pptx_render.py. В этой задаче фактически исполнялся собственный build_deck.py через указанное venv; он напрямую использует python-pptx и не вызывает LibreOffice.

## в) Полный текущий bootstrap_renderer.py

Скрипт запускает apt в режиме симуляции для расчёта зависимостей; скачивает выбранные версии в отдельный каталог; выполняет только dpkg-deb -x в частный prefix. Системная установка, регистрация пакетов и maintainer scripts не выполняются. Затем запускает проверку версии LibreOffice.

Важно: текущий файл уже содержит дополненные пути библиотек. Все последующие ручные поправки частных конфигураций перечислены ниже; bootstrap сам по себе ещё не является воспроизводимым успешным установщиком. Перезапуск распаковки способен перезаписать эти частные поправки.

```python
"""Owner-approved rootless unpacking of renderer dependencies. No dpkg install/configure."""
from pathlib import Path
import subprocess,re,os,json
ROOT=Path('/var/lib/hermes/workspace/tools/presentations')
CONF=ROOT/'apt.conf';PKGS=ROOT/'packages';PREFIX=ROOT/'runtime'
base=['apt-get','-c',str(CONF)]
sim=subprocess.run(base+['-s','install','--no-install-recommends','libreoffice-impress','fonts-liberation','fonts-noto-mono'],capture_output=True,text=True,check=True)
packages=[a+'='+b for a,b in re.findall(r'^Inst (\S+) \((\S+)',sim.stdout,re.M)]
assert packages and os.getuid()!=0
subprocess.run(base+['download',*packages],cwd=PKGS,check=True)
archives=sorted(PKGS.glob('*.deb'))
assert len(archives)==len(packages),(len(archives),len(packages))
for i,p in enumerate(archives,1):
 subprocess.run(['dpkg-deb','-x',str(p),str(PREFIX)],check=True)
print('PRIVATE_DEB_EXTRACTION_COMPLETE',len(archives),flush=True)
env=os.environ.copy()
env['LD_LIBRARY_PATH']=':'.join(map(str,[PREFIX/'lib/x86_64-linux-gnu',PREFIX/'usr/lib/x86_64-linux-gnu',PREFIX/'usr/lib/libreoffice/program',PREFIX/'usr/lib',PREFIX/'lib']))
env['FONTCONFIG_FILE']=str(ROOT/'fonts.conf')
env['XDG_CACHE_HOME']=str(ROOT/'cache')
env['SAL_USE_VCLPLUGIN']='svp'
lo=PREFIX/'usr/lib/libreoffice/program/soffice'
p=subprocess.run([str(lo),'--headless','-env:UserInstallation='+ (ROOT/'lo-profile').as_uri(),'--version'],env=env,capture_output=True,text=True,timeout=45)
print('RENDERER_PROBE_EXIT',p.returncode,'STDOUT',p.stdout,'STDERR',p.stderr,flush=True)
(ROOT/'runtime-manifest.json').write_text(json.dumps({'packages':packages,'prefix':str(PREFIX),'renderer':str(lo),'probe_exit':p.returncode,'probe_stdout':p.stdout,'probe_stderr':p.stderr,'installation':'private unpack only; no package registration or maintainer scripts'},indent=2))
if p.returncode:raise SystemExit(p.returncode)

```

### Полный runtime_env.py

```python
"""Process-local renderer environment; does not export global variables."""
from pathlib import Path
import os,subprocess
ROOT=Path('/var/lib/hermes/workspace/tools/presentations')
PREFIX=ROOT/'runtime'
EXE=PREFIX/'usr/lib/libreoffice/program/soffice'
def environment():
    env=os.environ.copy()
    env['LD_LIBRARY_PATH']=':'.join(str(x) for x in [PREFIX/'lib/x86_64-linux-gnu',PREFIX/'usr/lib/x86_64-linux-gnu',PREFIX/'usr/lib/libreoffice/program',PREFIX/'usr/lib',PREFIX/'lib'])
    env['FONTCONFIG_FILE']=str(ROOT/'fonts.conf')
    env['XDG_CACHE_HOME']=str(ROOT/'cache')
    env['SAL_USE_VCLPLUGIN']='svp'
    return env
if __name__=='__main__':
    p=subprocess.run([str(EXE),'--headless','-env:UserInstallation='+(ROOT/'lo-profile').as_uri(),'--version'],env=environment(),capture_output=True,text=True,timeout=40)
    print('EXIT',p.returncode,p.stdout,p.stderr)
    raise SystemExit(p.returncode)

```

## г) Последний фактический запуск

Команда (эквивалент argv; без секретов):

```text
/var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/libreoffice/program/soffice --headless -env:UserInstallation=file:///var/lib/hermes/workspace/tools/presentations/lo-profile --version
```

Рабочий каталог: `/var/lib/hermes/workspace/projects/1c-digital-analyst-presentation`.

Необходимые параметры окружения переданы только дочернему процессу. Полного дампа окружения нет.

```json
{
  "HOME": "/home/athena",
  "TMPDIR": null,
  "TMP": null,
  "TEMP": null,
  "LD_LIBRARY_PATH": "/var/lib/hermes/workspace/tools/presentations/runtime/lib/x86_64-linux-gnu:/var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu:/var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/libreoffice/program:/var/lib/hermes/workspace/tools/presentations/runtime/usr/lib:/var/lib/hermes/workspace/tools/presentations/runtime/lib",
  "FONTCONFIG_FILE": "/var/lib/hermes/workspace/tools/presentations/fonts.conf",
  "XDG_CACHE_HOME": "/var/lib/hermes/workspace/tools/presentations/cache",
  "SAL_USE_VCLPLUGIN": "svp",
  "URE_BOOTSTRAP": null,
  "UNO_PATH": null
}
```

Полный stdout:
```text

```
Полный stderr:
```text

```
Оба потока пусты, если между границами блока ничего не напечатано. Код завершения: **139**. Код 139 соответствует аварийному завершению SIGSEGV в цепочке запуска; успешного запуска нет.

## д) DeploymentException и stack trace

В предыдущих запусках, до создания дополнительного private unorc, выводился следующий **полный фактически полученный stderr**:

```text
terminate called after throwing an instance of 'com::sun::star::uno::DeploymentException'

```

Код завершения тех запусков: 134. Дополнительный текст поля Message, сведения о конкретной фабрике UNO и C++ stack trace процесс не напечатал и они не были получены. **Stack trace отсутствует; он не заменён пересказом и не выдуман.** Последний запуск уже не выводит эту строку: stderr пуст и код 139. Нельзя выдавать исторический 134 за текущий результат.

Существующий renderer-file-trace.log — трассировка файловых обращений strace, НЕ C++ stack trace. В ней наблюдался отсутствующий usr/lib/x86_64-linux-gnu/unorc. Это подтверждает конкретный неудачный lookup, но само по себе не доказывает причину последующего SIGSEGV. Дампы памяти в отчёт не включаются из-за риска присутствия секретов. В последнем диагностическом дочернем процессе core dumps отключены локальным RLIMIT_CORE=(0,0).

## е) Зависимости доверенного soffice.bin

Проверялся только уже развёрнутый доверенный бинарный файл:

```json
{
  "path": "/var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/libreoffice/program/soffice.bin",
  "sha256": "49c0b1b896d10660ea223c00c45c91a72b94e8452bbf3b70b6b6d73957c05f20",
  "mode": "0o755",
  "uid": 10000
}
```

Команда:
```text
/usr/bin/ldd /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/libreoffice/program/soffice.bin
```

Полный stdout ldd:
```text
	linux-vdso.so.1 (0x00007fc87ec0a000)
	libuno_sal.so.3 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libuno_sal.so.3 (0x00007fc87eb95000)
	libmergedlo.so => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/libreoffice/program/libmergedlo.so (0x00007fc87a800000)
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007fc87a61e000)
	libz.so.1 => /lib/x86_64-linux-gnu/libz.so.1 (0x00007fc87eb74000)
	libstdc++.so.6 => /lib/x86_64-linux-gnu/libstdc++.so.6 (0x00007fc87a404000)
	libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x00007fc87a324000)
	libgcc_s.so.1 => /lib/x86_64-linux-gnu/libgcc_s.so.1 (0x00007fc87eb52000)
	/lib64/ld-linux-x86-64.so.2 (0x00007fc87ec0c000)
	libepoxy.so.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libepoxy.so.0 (0x00007fc87a1f5000)
	libgpgmepp.so.6 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libgpgmepp.so.6 (0x00007fc87eae5000)
	libicuuc.so.72 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libicuuc.so.72 (0x00007fc879ff7000)
	libnss3.so => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libnss3.so (0x00007fc879e9e000)
	libsmime3.so => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libsmime3.so (0x00007fc87eab4000)
	libplc4.so => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libplc4.so (0x00007fc87eaad000)
	libnspr4.so => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libnspr4.so (0x00007fc879e5c000)
	libdconf.so.1 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libdconf.so.1 (0x00007fc879e48000)
	libgio-2.0.so.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libgio-2.0.so.0 (0x00007fc879c68000)
	libgobject-2.0.so.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libgobject-2.0.so.0 (0x00007fc879c09000)
	libglib-2.0.so.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libglib-2.0.so.0 (0x00007fc879ad0000)
	libdbus-1.so.3 => /var/lib/hermes/workspace/tools/presentations/runtime/lib/x86_64-linux-gnu/libdbus-1.so.3 (0x00007fc879a7a000)
	libicui18n.so.72 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libicui18n.so.72 (0x00007fc879600000)
	libcurl-gnutls.so.4 => /lib/x86_64-linux-gnu/libcurl-gnutls.so.4 (0x00007fc8799d0000)
	libxml2.so.2 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libxml2.so.2 (0x00007fc879454000)
	libxslt.so.1 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libxslt.so.1 (0x00007fc87998d000)
	libexslt.so.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libexslt.so.0 (0x00007fc879975000)
	libexpat.so.1 => /lib/x86_64-linux-gnu/libexpat.so.1 (0x00007fc879949000)
	libclucene-core.so.1 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libclucene-core.so.1 (0x00007fc8792b4000)
	libclucene-contribs-lib.so.1 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libclucene-contribs-lib.so.1 (0x00007fc879251000)
	libexttextcat-2.0.so.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libexttextcat-2.0.so.0 (0x00007fc879000000)
	libhunspell-1.7.so.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libhunspell-1.7.so.0 (0x00007fc878f89000)
	libhyphen.so.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libhyphen.so.0 (0x00007fc879942000)
	libmythes-1.2.so.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libmythes-1.2.so.0 (0x00007fc87993d000)
	libnumbertext-1.0.so.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libnumbertext-1.0.so.0 (0x00007fc878f36000)
	liborcus-0.17.so.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/liborcus-0.17.so.0 (0x00007fc878df0000)
	libboost_locale.so.1.74.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libboost_locale.so.1.74.0 (0x00007fc878d0c000)
	librdf.so.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/librdf.so.0 (0x00007fc879214000)
	libraptor2.so.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libraptor2.so.0 (0x00007fc878ca7000)
	libgraphite2.so.3 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libgraphite2.so.3 (0x00007fc878c7d000)
	libharfbuzz-icu.so.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libharfbuzz-icu.so.0 (0x00007fc879936000)
	libharfbuzz.so.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libharfbuzz.so.0 (0x00007fc878b79000)
	liblcms2.so.2 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/liblcms2.so.2 (0x00007fc878b16000)
	libeot.so.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libeot.so.0 (0x00007fc878b06000)
	libjpeg.so.62 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libjpeg.so.62 (0x00007fc878a73000)
	libpng16.so.16 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libpng16.so.16 (0x00007fc878a3d000)
	libtiff.so.6 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libtiff.so.6 (0x00007fc8789b1000)
	libwebp.so.7 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libwebp.so.7 (0x00007fc87893f000)
	libX11.so.6 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libX11.so.6 (0x00007fc8787fd000)
	libXext.so.6 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libXext.so.6 (0x00007fc8787e8000)
	libcairo.so.2 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libcairo.so.2 (0x00007fc8786c4000)
	libcups.so.2 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libcups.so.2 (0x00007fc878627000)
	libfontconfig.so.1 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libfontconfig.so.1 (0x00007fc8785dc000)
	libfreetype.so.6 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libfreetype.so.6 (0x00007fc878512000)
	libuno_cppu.so.3 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libuno_cppu.so.3 (0x00007fc8784e5000)
	libuno_cppuhelpergcc3.so.3 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libuno_cppuhelpergcc3.so.3 (0x00007fc878406000)
	libi18nlangtag.so => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/libreoffice/program/libi18nlangtag.so (0x00007fc8783e1000)
	libjvmaccesslo.so => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/libreoffice/program/libjvmaccesslo.so (0x00007fc87920b000)
	libjvmfwklo.so => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/libreoffice/program/libjvmfwklo.so (0x00007fc8783c1000)
	libuno_salhelpergcc3.so.3 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libuno_salhelpergcc3.so.3 (0x00007fc8783b8000)
	libxmlreaderlo.so => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/libreoffice/program/libxmlreaderlo.so (0x00007fc8783ad000)
	libclewlo.so => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/libreoffice/program/libclewlo.so (0x00007fc8783a6000)
	libskialo.so => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/libreoffice/program/libskialo.so (0x00007fc877c00000)
	libpdfiumlo.so => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/libreoffice/program/libpdfiumlo.so (0x00007fc877800000)
	libdl.so.2 => /lib/x86_64-linux-gnu/libdl.so.2 (0x00007fc879206000)
	libgpgme.so.11 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libgpgme.so.11 (0x00007fc878352000)
	libicudata.so.72 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libicudata.so.72 (0x00007fc875a00000)
	libnssutil3.so => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libnssutil3.so (0x00007fc877bce000)
	libplds4.so => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libplds4.so (0x00007fc87834d000)
	libgmodule-2.0.so.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libgmodule-2.0.so.0 (0x00007fc878347000)
	libmount.so.1 => /lib/x86_64-linux-gnu/libmount.so.1 (0x00007fc87599d000)
	libselinux.so.1 => /lib/x86_64-linux-gnu/libselinux.so.1 (0x00007fc877ba0000)
	libffi.so.8 => /lib/x86_64-linux-gnu/libffi.so.8 (0x00007fc878339000)
	libpcre2-8.so.0 => /lib/x86_64-linux-gnu/libpcre2-8.so.0 (0x00007fc875903000)
	libsystemd.so.0 => /lib/x86_64-linux-gnu/libsystemd.so.0 (0x00007fc875833000)
	libnghttp2.so.14 => /lib/x86_64-linux-gnu/libnghttp2.so.14 (0x00007fc875804000)
	libidn2.so.0 => /lib/x86_64-linux-gnu/libidn2.so.0 (0x00007fc8757d3000)
	librtmp.so.1 => /lib/x86_64-linux-gnu/librtmp.so.1 (0x00007fc8777df000)
	libssh2.so.1 => /lib/x86_64-linux-gnu/libssh2.so.1 (0x00007fc875792000)
	libpsl.so.5 => /lib/x86_64-linux-gnu/libpsl.so.5 (0x00007fc87577e000)
	libnettle.so.8 => /lib/x86_64-linux-gnu/libnettle.so.8 (0x00007fc875730000)
	libgnutls.so.30 => /lib/x86_64-linux-gnu/libgnutls.so.30 (0x00007fc875511000)
	libgssapi_krb5.so.2 => /lib/x86_64-linux-gnu/libgssapi_krb5.so.2 (0x00007fc8754be000)
	libldap-2.5.so.0 => /lib/x86_64-linux-gnu/libldap-2.5.so.0 (0x00007fc87545f000)
	liblber-2.5.so.0 => /lib/x86_64-linux-gnu/liblber-2.5.so.0 (0x00007fc87544f000)
	libzstd.so.1 => /lib/x86_64-linux-gnu/libzstd.so.1 (0x00007fc875393000)
	libbrotlidec.so.1 => /lib/x86_64-linux-gnu/libbrotlidec.so.1 (0x00007fc875386000)
	liblzma.so.5 => /lib/x86_64-linux-gnu/liblzma.so.5 (0x00007fc875357000)
	libgcrypt.so.20 => /lib/x86_64-linux-gnu/libgcrypt.so.20 (0x00007fc875210000)
	libclucene-shared.so.1 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libclucene-shared.so.1 (0x00007fc8751ed000)
	libpthread.so.0 => /lib/x86_64-linux-gnu/libpthread.so.0 (0x00007fc8777d6000)
	liborcus-parser-0.17.so.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/liborcus-parser-0.17.so.0 (0x00007fc87519d000)
	libboost_filesystem.so.1.74.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libboost_filesystem.so.1.74.0 (0x00007fc87517c000)
	libboost_iostreams.so.1.74.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libboost_iostreams.so.1.74.0 (0x00007fc875164000)
	libboost_thread.so.1.74.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libboost_thread.so.1.74.0 (0x00007fc875141000)
	librasqal.so.3 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/librasqal.so.3 (0x00007fc8750c5000)
	libltdl.so.7 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libltdl.so.7 (0x00007fc8750ba000)
	libdb-5.3.so => /lib/x86_64-linux-gnu/libdb-5.3.so (0x00007fc874ef8000)
	libyajl.so.2 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libyajl.so.2 (0x00007fc874eec000)
	libLerc.so.4 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libLerc.so.4 (0x00007fc874e54000)
	libjbig.so.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libjbig.so.0 (0x00007fc874e43000)
	libdeflate.so.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libdeflate.so.0 (0x00007fc874e1d000)
	libxcb.so.1 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libxcb.so.1 (0x00007fc874df1000)
	libpixman-1.so.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libpixman-1.so.0 (0x00007fc874d46000)
	libxcb-shm.so.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libxcb-shm.so.0 (0x00007fc874d41000)
	libxcb-render.so.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libxcb-render.so.0 (0x00007fc874d33000)
	libXrender.so.1 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libXrender.so.1 (0x00007fc874d26000)
	libavahi-common.so.3 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libavahi-common.so.3 (0x00007fc874d16000)
	libavahi-client.so.3 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libavahi-client.so.3 (0x00007fc874d03000)
	libreglo.so => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/libreoffice/program/libreglo.so (0x00007fc874ce7000)
	libunoidllo.so => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/libreoffice/program/libunoidllo.so (0x00007fc874c8c000)
	liblangtag.so.1 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/liblangtag.so.1 (0x00007fc874c65000)
	libX11-xcb.so.1 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libX11-xcb.so.1 (0x00007fc874c5e000)
	libopenjp2.so.7 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libopenjp2.so.7 (0x00007fc874bfa000)
	libabsl_bad_optional_access.so.20220623 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libabsl_bad_optional_access.so.20220623 (0x00007fc874bf5000)
	libassuan.so.0 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libassuan.so.0 (0x00007fc874bdf000)
	libgpg-error.so.0 => /lib/x86_64-linux-gnu/libgpg-error.so.0 (0x00007fc874bb7000)
	libblkid.so.1 => /lib/x86_64-linux-gnu/libblkid.so.1 (0x00007fc874b5e000)
	libcap.so.2 => /lib/x86_64-linux-gnu/libcap.so.2 (0x00007fc874b52000)
	liblz4.so.1 => /lib/x86_64-linux-gnu/liblz4.so.1 (0x00007fc874b2c000)
	libunistring.so.2 => /lib/x86_64-linux-gnu/libunistring.so.2 (0x00007fc874976000)
	libhogweed.so.6 => /lib/x86_64-linux-gnu/libhogweed.so.6 (0x00007fc87492d000)
	libgmp.so.10 => /lib/x86_64-linux-gnu/libgmp.so.10 (0x00007fc8748aa000)
	libcrypto.so.3 => /lib/x86_64-linux-gnu/libcrypto.so.3 (0x00007fc874420000)
	libp11-kit.so.0 => /lib/x86_64-linux-gnu/libp11-kit.so.0 (0x00007fc8742ec000)
	libtasn1.so.6 => /lib/x86_64-linux-gnu/libtasn1.so.6 (0x00007fc8742d7000)
	libkrb5.so.3 => /lib/x86_64-linux-gnu/libkrb5.so.3 (0x00007fc8741fd000)
	libk5crypto.so.3 => /lib/x86_64-linux-gnu/libk5crypto.so.3 (0x00007fc8741ce000)
	libcom_err.so.2 => /lib/x86_64-linux-gnu/libcom_err.so.2 (0x00007fc8741c8000)
	libkrb5support.so.0 => /lib/x86_64-linux-gnu/libkrb5support.so.0 (0x00007fc8741ba000)
	libsasl2.so.2 => /lib/x86_64-linux-gnu/libsasl2.so.2 (0x00007fc87419d000)
	libbrotlicommon.so.1 => /lib/x86_64-linux-gnu/libbrotlicommon.so.1 (0x00007fc87417a000)
	libbz2.so.1.0 => /lib/x86_64-linux-gnu/libbz2.so.1.0 (0x00007fc874165000)
	libmhash.so.2 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libmhash.so.2 (0x00007fc874137000)
	libuuid.so.1 => /lib/x86_64-linux-gnu/libuuid.so.1 (0x00007fc87412d000)
	libXau.so.6 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libXau.so.6 (0x00007fc874128000)
	libXdmcp.so.6 => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/libXdmcp.so.6 (0x00007fc873e00000)
	libstorelo.so => /var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/libreoffice/program/libstorelo.so (0x00007fc87410c000)
	libkeyutils.so.1 => /lib/x86_64-linux-gnu/libkeyutils.so.1 (0x00007fc874105000)
	libresolv.so.2 => /lib/x86_64-linux-gnu/libresolv.so.2 (0x00007fc8740f4000)
	libbsd.so.0 => /lib/x86_64-linux-gnu/libbsd.so.0 (0x00007fc8740de000)
	libmd.so.0 => /lib/x86_64-linux-gnu/libmd.so.0 (0x00007fc8740cf000)

```
Полный stderr ldd:
```text

```

Код ldd: 0. Строк not found: 0. Полные пути найденных библиотек приведены в выводе выше. Часть библиотек берётся из частного prefix, часть — из базовой системы.

Отсутствие missing в ldd **не доказывает** корректность UNO bootstrap, реестров компонентов, позднего dlopen, шрифтов и фильтров экспорта. Отдельная проверка libmergedlo.so ранее также не выявила not found; запуск всё равно не прошёл.

## ж) Профили, HOME, временный каталог и параллельность

Проверялись только необходимые пути. Для существующих доступных каталогов выполнялась запись собственного временного файла с немедленным удалением; отсутствующие каталоги не создавались специально.

```json
[
  {
    "path": "/home/athena",
    "exists": true,
    "is_directory": true,
    "write_probe": "created_and_removed_own_temporary_file",
    "os_access_write": true
  },
  {
    "path": "/tmp",
    "exists": true,
    "is_directory": true,
    "write_probe": "created_and_removed_own_temporary_file",
    "os_access_write": true
  },
  {
    "path": "/var/lib/hermes/workspace/tools/presentations/lo-profile",
    "exists": false,
    "is_directory": false,
    "write_probe": "not_run",
    "nearest_existing_parent": "/var/lib/hermes/workspace/tools/presentations"
  },
  {
    "path": "/var/lib/hermes/workspace/tools/presentations/diagnostic-profile",
    "exists": false,
    "is_directory": false,
    "write_probe": "not_run",
    "nearest_existing_parent": "/var/lib/hermes/workspace/tools/presentations"
  },
  {
    "path": "/var/lib/hermes/workspace/tools/presentations/diagnostic-profile-2",
    "exists": false,
    "is_directory": false,
    "write_probe": "not_run",
    "nearest_existing_parent": "/var/lib/hermes/workspace/tools/presentations"
  },
  {
    "path": "/var/lib/hermes/workspace/tools/presentations/trace-profile",
    "exists": false,
    "is_directory": false,
    "write_probe": "not_run",
    "nearest_existing_parent": "/var/lib/hermes/workspace/tools/presentations"
  },
  {
    "path": "/var/lib/hermes/workspace/tools/presentations/lo-profile/user",
    "exists": false,
    "is_directory": false,
    "write_probe": "not_run",
    "nearest_existing_parent": "/var/lib/hermes/workspace/tools/presentations"
  },
  {
    "path": "/var/lib/hermes/workspace/tools/presentations",
    "exists": true,
    "is_directory": true,
    "write_probe": "created_and_removed_own_temporary_file",
    "os_access_write": true
  }
]
```

Эффективный временный каталог: `/tmp`.

Процессы renderer того же пользователя после контрольного запуска:
```json
[]
```

Это снимок текущего состояния. Он не доказывает отсутствия пересечений профилей в прошлом. Проверка повторного успешного запуска пока невозможна: исходный запуск не проходит.

## з) Уже выполненные изменения

- `/var/lib/hermes/workspace/tools/presentations/bootstrap_renderer.py`: LD_LIBRARY_PATH extended with private runtime/lib/x86_64-linux-gnu and runtime/lib; originally only usr/lib paths were included.
- `/var/lib/hermes/workspace/tools/presentations/runtime_env.py`: Process-local LD_LIBRARY_PATH, FONTCONFIG_FILE, XDG_CACHE_HOME and SAL_USE_VCLPLUGIN=svp; no global environment export.
- `/var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/libreoffice/program/fundamentalrc`: BRAND_BASE_DIR and CONFIGURATION_LAYERS changed from system locations to the private unpacked prefix.
- `/var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/libreoffice/program/sofficerc`: FHS_CONFIG_FILE relocated to private etc/libreoffice/sofficerc.
- `/var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/libreoffice/share`: Four absolute symlinks for registry, psprint.conf, uno_packages/cache and prereg/bundled were redirected to corresponding files under the private prefix.
- `/var/lib/hermes/workspace/tools/presentations/runtime/usr/lib/x86_64-linux-gnu/unorc`: New private UNO bootstrap file created after strace observed missing unorc next to loaded UNO libraries. Subsequent version probe changed from exit 134 to exit 139; this is NOT a successful fix.
- `/var/lib/hermes/workspace/tools/presentations/apt.conf`: Private apt lists/cache/log paths; post-invoke cleanup hooks cleared after an initial system-cache cleanup attempt returned Permission denied. No successful system-cache deletion is established.
- `/var/lib/hermes/workspace/tools/presentations/runtime/usr/bin/strace`: Diagnostic strace package unpacked privately before the latest no-more-packages instruction; no packages added by this collection.

### Что установлено о причине

1. Первая ошибка exit 127 была связана с поиском libdbus-1.so.3: библиотека распакована в private runtime/lib/x86_64-linux-gnu, который изначально отсутствовал в LD_LIBRARY_PATH. После добавления пути этот исходный loader error перестал выводиться.
2. Debian-пакеты были распакованы как файлы без штатной системной установки. В них обнаружены ссылки на системные /etc и /var и абсолютные bootstrap-пути, которые пришлось перенаправлять внутри private prefix. Поэтому это пока не готовый переносной runtime.
3. Точная причина текущего SIGSEGV **не установлена**. Корреляция с добавлением private unorc — повод для контролируемой проверки, не доказательство причины. Версия о необходимости графического экрана данными не подтверждена. Падение происходит на --version до открытия презентации.
4. Создание PPTX в python-pptx работает отдельно. Сбой renderer не является ошибкой содержимого PPTX.

## Следующие варианты — только предложения, НЕ выполненные изменения

### А. Минимальный путь для существующего renderer

Доказанного однострочного исправления текущего кода 139 нет. Минимальный обоснованный путь — отдельная диагностическая копия текущего private prefix: сохранить хеши и исходные файлы, восстановить штатную конфигурацию URE из уже скачанных пакетов, затем согласовать один способ поиска unorc/реестров и библиотек вместо нескольких параллельных переопределений. Проверить гипотезу о переходе 134 → 139 изменением только добавленного private unorc в этой копии. Не менять рабочую систему и не переустанавливать пакеты вслепую.
Состав: копия частного runtime; фиксация исходного состояния; проверка unorc, fundamentalrc и переменных запуска; отдельный профиль. Для определения точной причины SIGSEGV может потребоваться согласованный отладчик и C++ backtrace. Сейчас дополнительные средства не устанавливались.
Риски: неполная релокация Debian runtime, сложность воспроизведения, новые ошибки после обхода текущей. Результат может оказаться отрицательным. Откат: удалить только созданную диагностическую копию после согласования, оставить исходный snapshot и существующий Python-генератор без изменений. Нельзя называть этот откат восстановлением renderer.

### Б. Отдельное воспроизводимое окружение рендеринга — предпочтительное для регулярной работы

Подготовить отдельный образ/контейнер renderer со штатно установленными внутри него LibreOffice Impress и нужными шрифтами; версии и базовый образ закрепить при согласованной сборке. Не использовать эту среду как движок Excel-моделей и не передавать Docker socket агенту. Входной PPTX монтировать только на чтение, выход — в отдельный каталог; runtime без сети, без root и с ограничением ресурсов. Для каждого задания отдельный профиль LibreOffice и временная папка.
Состав изменений: новый image/build recipe и узкий вызов конвертера с хоста либо разрешённого исполнителя. Основной Hermes, его модель, инструменты и рабочие Excel-файлы не менять. Docker в текущем SSH executor не предполагается доступным; способ запуска и административное действие на хосте потребуют отдельного согласования.
Риски: объём образа, сопровождение обновлений, различия рендеринга с Microsoft PowerPoint и шрифтов. Откат: прекратить использование только нового renderer, вернуть статус PDF unavailable; не трогать прочие контейнеры и файлы. Внешние облачные сервисы не подключать.

### Критерии приёмки восстановления

- LibreOffice проходит проверку запуска с кодом 0.
- Доверенный тестовый PPTX конвертируется в настоящий непустой PDF.
- Число страниц PDF совпадает с числом слайдов.
- Все страницы преобразованы в PNG существующим pypdfium2.
- Проверены русский текст, шрифты, переносы, обрезка и наложения на отрисованных страницах.
- Повторный запуск проходит с отдельным профилем без конфликтов и без изменения входного PPTX.
- Сохранены команды, exit codes, логи и хеши результата.

Ни вариант А, ни вариант Б в рамках этой диагностики не выполнялся. **До изменения инфраструктуры требуется подтверждение Андрея.**

## Приложения

В ZIP-пакете: diagnostic.json, полный bootstrap_renderer.py.txt, runtime_env.py.txt, полные stdout/stderr контрольного запуска и ldd. Отчёт не содержит API-ключей, токенов или полного дампа окружения.